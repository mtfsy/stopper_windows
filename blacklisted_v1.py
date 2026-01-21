import psutil
import os
import time, sys, subprocess
import functools
from functools import partial
import argparse
import io

LOG_FILE = "activity_log.txt"

def task_report(name, log_filename=LOG_FILE, is_critical=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            status_ok = True
            result = None

            capture_output = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = capture_output

            try:
                # 1. Execute the function
                result = func(*args, **kwargs)
                
                # 2. Format the report based on return type
                if isinstance(result, list):
                    content = "\n".join(f"  • {item}" for item in result)
                    report = f"📋 {name} Results:\n{content}"
                elif isinstance(result, str):
                    report = f"ℹ️ {name}: {result}"
                else:
                    report = f"✅ {name}: Completed successfully."
                    
            except Exception as e:
                # 3. Catch and format errors
                status_ok = False
                report = f"❌ {name} FAILED: {str(e)}"

            finally:
                sys.stdout = old_stdout
            
            output_text = capture_output.getvalue().strip()
            #4 --- Logging Phase ---
            full_log = f"Time: [{timestamp}]--Task: {name}\n"
            if output_text:
                full_log += f"{output_text}\n"
                if result is not None and str(result) not in output_text:
                    full_log += f"Summary: {result}\n"
            elif result is not None:
                full_log += f"Result: {result}\n"
            else:
                full_log += "Execution completed (No Output). \n"
            full_log += "-" * 30 + "\n"

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(full_log)
                
                # If it's a critical failure, log the exit event specifically
                if not status_ok and is_critical:
                    exit_msg = f"[{timestamp}] 🛑 CRITICAL FAILURE: Terminating script to prevent errors.\n"
                    f.write(exit_msg)
                    f.flush() # Ensure it writes to disk before exit
                    sys.exit(1)
            
            return result # Return the original result if needed elsewhere
        return wrapper
    return decorator

@task_report("is_program_running")
def is_program_running(program_list):
    """
    Checks if any program from a given list is currently running.

    Args:
        program_list (list): A list of executable program names.

    Returns:
        A dictionary mapping running program names to their process objects.
    """
    running_processes = {}
    for process in psutil.process_iter(['name']):
        if process.info['name'] in program_list:
            running_processes[process.info['name']] = process
    print (running_processes)
    return running_processes

@task_report("kill_program")
def kill_program(program_name: str) -> str:
    """
    Terminated a specific program and returns a status message.
    """
    if os.name == 'nt':  # Windows Logic
        # Using subprocess to capture 'taskkill' output
        process = subprocess.run(
            ['taskkill', '/f', '/im', program_name],
            capture_output=True,
            text=True
        )
        
        if process.returncode == 0:
            return f"✅ SUCCESS: '{program_name}' terminated."
        else:
            # Captures "ERROR: The process ... not found."
            error_msg = process.stderr.strip() or process.stdout.strip()
            return f"❌ FAILED: '{program_name}' -> {error_msg}"

    else:  # Linux/Mac Logic (keeping psutil but returning string)
        try:
            for proc in psutil.process_iter(['name']):
                if proc.info['name'] == program_name:
                    proc.terminate()
                    return f"✅ SUCCESS: '{program_name}' terminated via psutil."
            return f"❌ INFO: '{program_name}' was not running."
        except Exception as e:
            return f"❌ ERROR: Could not kill '{program_name}': {e}"

@task_report("Check Requirements", is_critical=True)
def check_req(file_path: str):
    # 1. Check if file exists
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File '{file_path}' not found.")

    # 2. Check file size (5MB = 5 * 1024 * 1024 bytes)
    max_size = 5 * 1024 * 1024
    if os.path.getsize(file_path) > max_size:
        raise ValueError("File is larger than 5MB.")

    # 3. Check if it is a .txt file
    if not file_path.lower().endswith('.txt'):
        raise TypeError("File must be a .txt file.")

    # 4. Check integrity/corruption (Can it be opened and read as UTF-8?)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # We read a small chunk to check for basic encoding/corruption 
            # instead of loading 5MB into memory at once
            file.read(1024) 
    except (UnicodeDecodeError, IOError):
        raise RuntimeError("File is corrupted or unreadable.")

    return "Success: File meets all requirements."

@task_report("Log Cleaner")
def cleanup_logs(log_file_path: str):
    with open(log_file_path, 'w') as f:
        f.write(f"--- Log Wiped at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
    return "🧹 Activity log has been wiped."

@task_report("Single Loop")
def start_single_loop(task_function, interval_seconds: int):
    print(f"🛡️ Monitoring started. Interval: {interval_seconds}s. Ctrl+C to stop.")
    try:
        while True:
            # Execute the function and CATCH the return value
            report = task_function()
            
            # If the function returned text, print it and add a timestamp
            if report:
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                print(f"\n--- Report at {timestamp} ---")
                print(report)
            
            time.sleep(interval_seconds)
    except KeyboardInterrupt:
        print("\nStopping monitor...")
        sys.exit(0)

@task_report("Multi Process Loop")
def start_multi_scheduler(tasks: list):
    # Set the start time of the scheduler
    start_time = time.time()
    print(f" Scheduler Started at {time.strftime('%H:%M:%S')}")
    
    try:
        while True:
            current_time = time.time()
            for task in tasks:
                
                if task.get('is_first_run', False):
                    # Check if the initial delay has passed since the script started
                    if current_time - start_time >= task.get('first_run_delay', 0):
                        execute_task(task, current_time)
                        task['is_first_run'] = False # Disable first-run mode
                else:
                    # Normal interval logic
                    if current_time - task['last_run'] >= task['interval']:
                        execute_task(task, current_time)
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")

@task_report("Execute Task")
def execute_task(task, current_time):
    """Helper function to run the task and log it"""
    task['func']() # The decorator inside 'func' handles the file writing
    task['last_run'] = current_time

@task_report("Service Monitor")
def kill_svc_program(svc_process_terminate: list):
    results = []
    for svc in svc_process_terminate:
        process = subprocess.run(['net', 'stop', svc, '/y'], capture_output=True, text=True)
        status = f"[SUCCESS] {svc} stopped." if process.returncode == 0 else f"[INFO] {svc}: {process.stderr.strip()}"
        results.append(status)
    return results

@task_report("EXE Monitor")
def kill_exe_program(program_terminate: list):
    active_processes = is_program_running(program_terminate)
    
    if not active_processes:
        return "All programs are currently stopped."
        
    results = []
    for program in active_processes:
        status = kill_program(program)
        results.append(status)
    return results 

@task_report("Generate Task List")
def create_task_list(job_definitions):
    """
    job_definitions: (name, function, data_list, interval, first_delay)
    """
    return [
        {
            'name': name,
            'func': partial(func, data),
            'interval': interval,
            'first_run_delay': first_delay,
            'last_run': time.time(),
            'is_first_run': True if first_delay > 0 else False
        }
        for name, func, data, interval, first_delay in job_definitions
    ]

@task_report("Main")
def main():
    # 1. Setup the Argument Parser
    parser = argparse.ArgumentParser(description="Stopper")
    
    # Add arguments with default values
    parser.add_argument('--interval-svc', type=int, default=180, 
                        help='Interval between checks in seconds (default: 30)')

    parser.add_argument('--interval-exe', type=int, default=180, 
                        help='Interval between checks in seconds (default: 30)')
    
    parser.add_argument('--delay', type=int, default=86400, 
                        help='Initial delay before first run in seconds (default: 0)')
    
    args = parser.parse_args()

    check_req("text_program_to_be_blocked.txt")

    with open("text_program_to_be_blocked.txt") as txt:
        lines = txt.read().splitlines()
    
    prgm_list = [line for line in lines if line.lower().endswith('.exe')]
    svc_list = [line for line in lines if not line.lower().endswith('.exe') and line.strip()]

    jobs_to_make = [
        ('svc program', kill_svc_program, svc_list, args.interval_svc, 2),
        ('exe program', kill_exe_program, prgm_list, args.interval_exe, 1),
        ('Log Auto-Wipe', cleanup_logs, "activity_log.txt", args.delay, args.delay)
    ]
    my_tasks = create_task_list(jobs_to_make)                           
    start_multi_scheduler(my_tasks)

#need to do list
#1. create a log system
# . implement error reporting function
# . implement writting error function
#2. option to operation mode one time and continously
#3. log viewer ui/web
#4. improving performance using costum database you need to bouild
#5. creating save file using your costume data header/binary to improve efficiancy

#1.1 make every exe or svc process it own subprocess and add parameter on config file for how long to run and delay into txt file
#2.1 make log file have 1000 line if at 950 remove first 100 line at begining
#php make web related like routing 
#c++ go make linux related like process ebpf etc

if __name__ == "__main__":
    main()

    


    
	
    
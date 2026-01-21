import psutil
import os
import time, sys, subprocess
from functools import partial

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
    return running_processes

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

def check_req(file_path: str) -> tuple[bool, str]:
    # 1. Check if file exists
    if not os.path.exists(file_path):
        return False, "Error: File does not exist."

    # 2. Check file size (5MB = 5 * 1024 * 1024 bytes)
    max_size = 5 * 1024 * 1024
    if os.path.getsize(file_path) > max_size:
        return False, "Error: File is larger than 5MB."

    # 3. Check if it is a .txt file
    if not file_path.lower().endswith('.txt'):
        return False, "Error: Only .txt files are allowed."

    # 4. Check integrity/corruption (Can it be opened and read as UTF-8?)
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            # We read a small chunk to check for basic encoding/corruption 
            # instead of loading 5MB into memory at once
            file.read(1024) 
    except (UnicodeDecodeError, IOError):
        return False, "Error: File is corrupted or contains non-text data."

    return True, "Success: File meets all requirements."

def cleanup_logs(log_file_path: str) -> str:
    """Wipes the content of the log file."""
    try:
        with open(log_file_path, 'w') as f:
            f.write(f"--- Log Wiped at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        return "🧹 SUCCESS: Activity log has been wiped."
    except Exception as e:
        return f"❌ ERROR: Could not wipe log: {e}"

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

def start_multi_scheduler(tasks: list, log_filename="activity_log.txt"):
    # Set the start time of the scheduler
    start_time = time.time()
    print(f"🚀 Scheduler Started at {time.strftime('%H:%M:%S')}")
    
    try:
        while True:
            current_time = time.time()
            for task in tasks:
                
                if task.get('is_first_run', False):
                    # Check if the initial delay has passed since the script started
                    if current_time - start_time >= task.get('first_run_delay', 0):
                        execute_task(task, current_time, log_filename)
                        task['is_first_run'] = False # Disable first-run mode
                else:
                    # Normal interval logic
                    if current_time - task['last_run'] >= task['interval']:
                        execute_task(task, current_time, log_filename)
            
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping...")

def execute_task(task, current_time, log_filename):
    """Helper function to run the task and log it"""
    report = task['func']()
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"\n[{timestamp}] Task: {task['name']}\n{report}\n"
    
    print(log_entry)
    with open(log_filename, "a", encoding="utf-8") as f:
        f.write(log_entry)
        
    task['last_run'] = current_time

def kill_svc_program(svc_process_terminate: list) -> str:
    results = ["--- Service SVC Termination Log ---"]
    
    for svc in svc_process_terminate:
        # Use subprocess to catch the Windows output instead of printing it
        process = subprocess.run(
            ['net', 'stop', svc, '/y'], 
            capture_output=True, 
            text=True
        )
        
        # Check if it worked or why it failed
        if process.returncode == 0:
            status = f"[SUCCESS] {svc} stopped."
        else:
            # This captures "The Windows Update service is not started", etc.
            clean_error = process.stderr.strip() or process.stdout.strip()
            status = f"[INFO/ERROR] {svc}: {clean_error}"
        
        results.append(status)
    
    results.append("-------------------------------\n")
    return "\n".join(results)

def kill_exe_program(program_terminate: list) -> str:
    results = ["--- Service EXE Termination Log ---"]
    active_processes = is_program_running(program_terminate)
    
    if active_processes:
        #print("✅ The following program(s) from your list are currently running:")
        for program in active_processes:
            #print(f"- {program}")
            #print(f"\nAttempting to terminate '{program}'...")
            status = kill_program(program)
            results.append(status)
    else:
        results.append("All program has been stopped")
    
    return results

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



#need to do list
#1. create a log system
# . implement error reporting function
# . implement writting error function
#2. option to operation mode one time and continously
#3. log viewer ui/web
#4. improving performance using costum database you need to bouild
#5. creating save file using your costume data header/binary to improve efficiancy


if __name__ == "__main__":

    status, message = check_req("text_program_to_be_blocked.txt")

    if status is False:
        print(f"CRITICAL ERROR: {message}")
        sys.exit(1)  

    with open("text_program_to_be_blocked.txt") as txt:
        lines = txt.read().splitlines()
    
    prgm_list = [line for line in lines if line.lower().endswith('.exe')]
    svc_list = [line for line in lines if not line.lower().endswith('.exe') and line.strip()]

    #print (kill_svc_program(svc_list))
    #print (kill_exe_program(prgm_list))

    jobs_to_make = [
        ('svc program', kill_svc_program, svc_list, 180, 2),
        ('exe program', kill_exe_program, prgm_list, 180, 1),
        ('Log Auto-Wipe', cleanup_logs, "activity_log.txt", 3600, 5)
    ]

    my_tasks = create_task_list(jobs_to_make)                           
    #start_monitor_loop(lambda: kill_svc_program(svc_list), 180)
    start_multi_scheduler(my_tasks)


    
	
    
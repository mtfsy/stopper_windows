import psutil
import os
import time, sys, subprocess
import functools
from functools import partial
import argparse
import io

LOG_FILE = "activity_log.txt"

def task_report(name, is_critical=False):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
            capture_output = io.StringIO()
            old_stdout = sys.stdout
            sys.stdout = capture_output
            status_ok, result = True, None

            try:
                result = func(*args, **kwargs)
                if isinstance(result, list):
                    result = "\n" + "\n".join(f" • {str(item).strip()}" for item in result)
                elif isinstance(result, str):
                    result = result.strip()
            except Exception as e:
                status_ok, result = False, f"ERROR: {str(e)}"
            finally:
                sys.stdout = old_stdout

            output_text = capture_output.getvalue().strip()
            
            # Build clean log block
            log_parts = [f"[{timestamp}] TASK: {name}"]
            if output_text: log_parts.append(output_text)
            if result: log_parts.append(f"Result: {result}")
            log_entry = "\n".join(log_parts) + "\n" + "-"*30 + "\n"

            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(log_entry)
                if not status_ok and is_critical:
                    f.write(f"🛑 CRITICAL FAILURE. EXITING.\n")
                    sys.exit(1)
            
            print(log_entry.strip())
            return result
        return wrapper
    return decorator

class Task:
    def __init__(self, name, func, data, interval, delay):
        self.name = name
        self.action = partial(func, data) 
        self.interval = interval
        self.delay = delay
        self.last_run = time.time()
        self.is_first_run = delay > 0
        self.start_time = time.time()
    
    def should_run(self, current_time):
        if self.is_first_run:
            if current_time - self.start_time >= self.delay:
                return True
        else:
            if current_time - self.last_run >= self.interval:
                return True
        return False

    def run(self, current_time):
        self.action()
        self.last_run == current_time
        self.is_first_run = False

class StopperManager:
    @staticmethod
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
    
    @staticmethod
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
    
    @staticmethod
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

    @staticmethod
    @task_report("SVC Stopper")
    def kill_svc_program(svc_process_terminate: list):
        results = []
        for svc in svc_process_terminate:
            process = subprocess.run(['net', 'stop', svc, '/y'], capture_output=True, text=True)
            status = f"[SUCCESS] {svc} stopped." if process.returncode == 0 else f"[INFO] {svc}: {process.stderr.strip()}"
            results.append(status)
        return results

    @staticmethod
    @task_report("EXE Stopper")
    def kill_exe_program(program_terminate: list):
        active_processes = StopperManager.is_program_running(program_terminate)
        
        if not active_processes:
            return "All programs are currently stopped."
            
        results = []
        for program in active_processes:
            status = StopperManager.kill_program(program)
            results.append(status)
        return results 
    
    @staticmethod
    @task_report("Log Cleaner")
    def cleanup_logs(log_file_path: str):
        with open(log_file_path, 'w') as f:
            f.write(f"--- Log Wiped at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        return "🧹 Activity log has been wiped."

@task_report("Main")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval-svc', type=int, default=180)
    parser.add_argument('--interval-exe', type=int, default=180)
    parser.add_argument('--delay', type=int, default=86400)
    args = parser.parse_args()

    # Initial check
    StopperManager.check_req("text_program_to_be_blocked.txt")

    # Load file
    with open("text_program_to_be_blocked.txt") as f:
        lines = f.read().splitlines()
    
    exes = [l for l in lines if l.lower().endswith('.exe')]
    svcs = [l for l in lines if not l.lower().endswith('.exe') and l.strip()]

    # Create Task Objects
    tasks = [
        Task("SVC Monitor", StopperManager.kill_svc_program, svcs, args.interval_svc, 2),
        Task("EXE Monitor", StopperManager.kill_exe_program, exes, args.interval_exe, 1),
        Task("Log Wiper", StopperManager.cleanup_logs, LOG_FILE, args.delay, args.delay/2)
    ]

    print(f"🚀 Scheduler started at {time.strftime('%H:%M:%S')}")
    
    try:
        while True:
            now = time.time()
            for task in tasks:
                if task.should_run(now):
                    task.run(now)
            time.sleep(1)
    except KeyboardInterrupt:
        print("Shutting down...")




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

    


    
	
    
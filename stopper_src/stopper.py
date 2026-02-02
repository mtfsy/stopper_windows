import psutil, os, time, subprocess
from functools import partial
from .utils import task_report

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
    @task_report("Check Running Programs")
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
    @task_report("Programs Stopper")
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
                return f"SUCCESS: '{program_name}' terminated."
            else:
                # Captures "ERROR: The process ... not found."
                error_msg = process.stderr.strip() or process.stdout.strip()
                return f"FAILED: '{program_name}' -> {error_msg}"

        else:  # Linux/Mac Logic (keeping psutil but returning string)
            try:
                for proc in psutil.process_iter(['name']):
                    if proc.info['name'] == program_name:
                        proc.terminate()
                        return f"SUCCESS: '{program_name}' terminated via psutil."
                return f"INFO: '{program_name}' was not running."
            except Exception as e:
                return f"ERROR: Could not kill '{program_name}': {e}"

    @staticmethod
    @task_report("SVCs Stopper")
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
        active_processes = Task.is_program_running(program_terminate)
        
        if not active_processes:
            return "All programs are currently stopped."
            
        results = []
        for program in active_processes:
            status = Task.kill_program(program)
            results.append(status)
        return results 
    
    @staticmethod
    @task_report("Log Cleaner")
    def cleanup_logs(log_file_path: str):
        with open(log_file_path, 'w') as f:
            f.write(f"--- Log Wiped at {time.strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        return "🧹 Activity log has been wiped."

    


    
	
    
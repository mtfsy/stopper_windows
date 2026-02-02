import time, sys, functools, io, os


LOG_FILE = "activity_log.txt" 
BASE_DIR  = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LOG_PATH = os.path.join(BASE_DIR, "logs", LOG_FILE)


def task_report(name: str,  log_path:str=LOG_PATH, is_critical:bool=False):
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

            with open(log_path, "a", encoding="utf-8") as f:
                f.write(log_entry)
                if not status_ok and is_critical:
                    f.write(f"CRITICAL FAILURE. EXITING.\n")
                    sys.exit(1)
            
            print(log_entry.strip())
            return result
        return wrapper
    return decorator
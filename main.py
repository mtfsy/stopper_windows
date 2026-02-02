from stopper_src.stopper import Task
from stopper_src.utils import task_report
import argparse, time, sys, os


BASE_DIR  = os.path.dirname(os.path.abspath(__file__))

CONFIGS_FILE = "program_name.txt"
CONFIGS_PATH = os.path.join(BASE_DIR, "configs", CONFIGS_FILE)

LOG_FILE = "activity_log.txt" 
LOG_PATH = os.path.join(BASE_DIR, "logs", LOG_FILE)

@task_report("Main")
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--interval-svc', type=int, default=180)
    parser.add_argument('--interval-exe', type=int, default=180)
    parser.add_argument('--delay', type=int, default=86400)
    args = parser.parse_args()

    # Initial check
    Task.check_req(CONFIGS_PATH)

    # Load file
    with open(CONFIGS_PATH) as f:
        lines = f.read().splitlines()
    
    exes = [l for l in lines if l.lower().endswith('.exe')]
    svcs = [l for l in lines if not l.lower().endswith('.exe') and l.strip()]

    # Create Task Objects
    tasks = [
        Task("SVC Monitor", Task.kill_svc_program, svcs, args.interval_svc, 2),
        Task("EXE Monitor", Task.kill_exe_program, exes, args.interval_exe, 1),
        Task("Log Wiper", Task.cleanup_logs, LOG_PATH, args.delay, args.delay/2)
    ]

    print(f"Scheduler started at {time.strftime('%H:%M:%S')}")
    
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
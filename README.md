
**Stopper.exe** is a simple python script to terminate unwanted background tasks, telemetry services, and forced update programs on Windows.

## Features
- Targets both Windows Services (SVC) and Executables (EXE).
- Set how interval on both SVC and EXE timings."
- Keep activity log small using scheduled cleaning 
- Reads blocklist configs on every cycle without restart the script on background.
- Best use for windows using scheduler to start at every startup 

---

## 🛠 Usage

Run the program using main.py 

```bash
python main.py --interval-svc 180 --interval-exe 180 --delay 86400
```

or executables.


```bash
stopper.exe --interval-svc 180 --interval-exe 180 --delay 86400
```

Argument,Description,Default

--interval-svc,Frequency (in seconds) to check and stop listed SVC Services,180

--interval-exe,Frequency (in seconds) to check and kill listed Executables,180

--delay,Frequency (in seconds) to wipe/clear the activity_log.txt,86400

Configuration
The program looks for a file named program_name.txt in the configs folder relative to the executable. List the items you want to block, one per line.

Syntax Rules:
  1. Executables: Must end with .exe (e.g., TelemetryRunner.exe).
  2. Services: Must not have an extension (e.g., wuauserv).

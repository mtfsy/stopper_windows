
**Stopper.exe** is a lightweight system utility designed to automatically monitor and terminate unwanted background tasks, telemetry services, and forced update programs on Windows.

## 🚀 Features
- **Dual Monitoring:** Targets both Windows Services (SVC) and Executables (EXE).
- **Customizable Intervals:** Set how often the program checks for "annoyances."
- **Auto-Cleaning Logs:** Keeps track of blocked programs and wipes logs automatically based on your preferred schedule.
- **Dynamic Updates:** Reads your blocklist on every cycle—no need to restart the program to add new targets.

---

## 🛠 Usage

Run the program via Command Prompt or a shortcut. 

```bash
stopper.exe --interval-svc 180 --interval-exe 180 --delay 86400
```
Argument,Description,Default

--interval-svc,Frequency (in seconds) to check and stop listed Services.,180

--interval-exe,Frequency (in seconds) to check and kill listed Executables.,180

--delay,Frequency (in seconds) to wipe/clear the activity_log.txt.,86400

📂 Configuration
The program looks for a file named text_program_to_be_blocked.txt in the same folder as the executable. List the items you want to block, one per line.

Syntax Rules:
  1. Executables: Must end with .exe (e.g., TelemetryRunner.exe).
  2. Services: Must not have an extension (e.g., wuauserv).

⚙️Automated Setup (Recommended)
To ensure your environment stays clean automatically upon boot, use the Windows Task Scheduler:

  1. Create Task: Name it "System Stopper."
  2. Security Options: Check "Run with highest privileges" (Required to stop system services).
  3. Trigger: Set to "At log on" or "At system startup."
  4. Action: Point to stopper.exe and add your desired arguments (e.g., --interval-svc 60 --interval-exe 60).

📝 Logging & Monitoring
The utility generates an activity_log.txt file in its root directory. This log tracks:

  1. Every time a service is successfully stopped.
  2. Every time a process is terminated.
  3. The timestamp of when the log was last wiped (based on your --delay setting).

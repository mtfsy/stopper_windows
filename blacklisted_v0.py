import psutil
import os

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

def kill_program(program_name):
    """
    Terminates a specific program by its name.
    
    Args:
        program_name (str): The name of the executable program to terminate.
    """
    # Use os.kill on Windows for better compatibility if psutil.terminate() fails
    if os.name == 'nt':  # Check if the OS is Windows
        try:
            os.system(f'taskkill /f /im "{program_name}"')
            print(f"✅ Program '{program_name}' has been terminated using taskkill.")
            return True
        except Exception as e:
            print(f"❌ Failed to terminate '{program_name}' with taskkill. Reason: {e}")
            return False
    else:  # For non-Windows OS (Linux, macOS)
        found = False
        for proc in psutil.process_iter(['name']):
            if proc.info['name'] == program_name:
                try:
                    proc.terminate()  # Sends a SIGTERM signal
                    proc.wait(timeout=3) # Wait for the process to terminate
                    print(f"✅ Program '{program_name}' has been terminated.")
                    found = True
                    return True
                except psutil.NoSuchProcess:
                    # Process was already terminated
                    found = True
                    return True
                except Exception as e:
                    print(f"❌ Failed to terminate '{program_name}'. Reason: {e}")
                    found = True
                    return False
        if not found:
            print(f"❌ Program '{program_name}' is not running.")
            return False


if __name__ == "__main__":
    programs_to_check = ['OmenCommandCenterBackground.exe', 'NetworkCap.exe', 'AppHelperCap.exe', 'SysInfoCap.exe', 'HPCommRecovery.exe', 'DiagsCap.exe', 'MicrosoftEdgeUpdate.exe', 'hp-one-agent-service.exe', 'IntelAnalyticsService.exe', 'IntelConnectivityNetworkService.exe', 'IntelProviderDataHelperService.exe', 'ipfsvc.exe', 'OmenBGMonitor.exe', 'msedge.exe', 'HP.myHP.exe', 'HPSystemEventUtilityBackground.exe', 'HPSystemEventUtilityHost.exe']
	
    print('terminate update service')
    svc_process_terminate = ['wuauserv', 'UsoSvc']
    for process_service in svc_process_terminate:
        os.system(f'net stop "{process_service}"')
    
    # Check for running programs
    active_processes = is_program_running(programs_to_check)
    
    if active_processes:
        print("✅ The following program(s) from your list are currently running:")
        for program in active_processes:
            print(f"- {program}")
            print(f"\nAttempting to terminate '{program}'...")
            kill_program(program)
    else:
        print("❌ None of the programs in your list are currently running.")
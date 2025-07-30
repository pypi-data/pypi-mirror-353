"""Windows Chocolatey-based Docker installation operations."""
import subprocess
import ctypes
import sys
import os

def is_admin():
    """
    Check if the current process has admin privileges.
    
    Returns:
        bool: True if running with admin rights, False otherwise
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def is_chocolatey_installed():
    """
    Check if Chocolatey is installed.
    
    Returns:
        bool: True if Chocolatey is installed, False otherwise
    """
    try:
        result = subprocess.run(["choco", "--version"], capture_output=True, text=True)
        return result.returncode == 0
    except Exception:
        return False

def run_as_admin(command):
    """
    Attempt to run a command with admin privileges.
    
    Args:
        command (str): Command to run
    
    Returns:
        bool: True if command was launched, False otherwise
    """
    if is_admin():
        try:
            # If already admin, run the command directly
            subprocess.run(command, shell=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    # If not admin, use ShellExecute to elevate
    try:
        ctypes.windll.shell32.ShellExecuteW(
            None, 
            "runas", 
            sys.executable, 
            f'-c "import subprocess; subprocess.run(\'{command}\')"', 
            None, 
            1
        )
        return True
    except Exception as e:
        print(f"Failed to launch admin command: {e}")
        return False

def install_docker_chocolatey(lang):
    """
    Install Docker using Chocolatey.
    
    Args:
        lang (dict): Language translations
        
    Returns:
        bool: True if installation was initiated, False otherwise
    """
    # First, check if Chocolatey is installed
    if not is_chocolatey_installed():
        print(lang.get("choco_not_found", "Chocolatey not found. Please install it manually."))
        print("Visit https://chocolatey.org/install to install Chocolatey.")
        return False
    
    # Attempt to install Docker Desktop
    docker_install_cmd = "choco install docker-desktop -y"
    
    if run_as_admin(docker_install_cmd):
        print("\nAttempted to install Docker Desktop.")
        print("Please check the Command Prompt window for installation progress.")
        return True
    else:
        print("\nFailed to install Docker Desktop.")
        print(lang.get("docker_install_choco_instructions", 
              "IMPORTANT: Please run this command in an ADMINISTRATOR Command Prompt or PowerShell:"))
        print(lang.get("docker_install_choco_command", "choco install docker-desktop -y"))
        return False

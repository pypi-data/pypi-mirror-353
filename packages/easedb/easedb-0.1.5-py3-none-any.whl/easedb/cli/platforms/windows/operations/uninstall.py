"""Windows Docker uninstallation operations."""
import subprocess
from .chocolatey import is_chocolatey_installed

def stop_all_containers():
    """
    Stop and remove all Docker containers.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        # Stop all containers
        subprocess.run(["docker", "stop", "$(docker ps -a -q)"], 
                      shell=True, capture_output=True, text=True)
        
        # Remove all containers
        subprocess.run(["docker", "rm", "$(docker ps -a -q)"], 
                      shell=True, capture_output=True, text=True)
        return True
    except Exception:
        return False

def uninstall_docker_chocolatey():
    """
    Uninstall Docker using Chocolatey.
    
    Returns:
        bool: True if uninstallation was successful, False otherwise
    """
    try:
        subprocess.run(["choco", "uninstall", "docker-desktop", "-y"], check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def uninstall_docker_windows(lang):
    """
    Uninstall Docker on Windows.
    
    Args:
        lang (dict): Language translations
    """
    print(lang.get("uninstalling_docker_windows", "Uninstalling Docker on Windows..."))
    
    # First try to stop all containers
    if not stop_all_containers():
        print("Warning: Failed to stop all Docker containers.")
    
    # Try Chocolatey uninstallation if available
    if is_chocolatey_installed():
        if uninstall_docker_chocolatey():
            print("Docker Desktop uninstalled successfully. Please restart your computer.")
            return
        else:
            print("Failed to uninstall Docker Desktop using Chocolatey.")
    
    # Fallback to manual uninstallation instructions
    print("\nPlease uninstall Docker Desktop manually:")
    print("1. Open Control Panel")
    print("2. Go to Programs and Features")
    print("3. Find Docker Desktop and click Uninstall")
    print("4. Follow the uninstallation wizard")
    print("5. Restart your computer when done")

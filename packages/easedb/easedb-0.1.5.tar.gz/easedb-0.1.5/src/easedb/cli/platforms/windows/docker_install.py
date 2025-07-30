"""Windows Docker installation module."""
from .operations.chocolatey import install_docker_chocolatey
from .operations.manual import install_docker_manual
from .operations.uninstall import uninstall_docker_windows
from ..common.docker_utils import verify_docker_installation, get_docker_version

__all__ = ['install_docker_windows', 'uninstall_docker_windows']

def install_docker_windows(lang):
    """
    Main Docker installation method for Windows.
    
    Args:
        lang (dict): Language translations
    """
    # Check if Docker is already installed
    current_version = get_docker_version()
    if current_version:
        print(f"\nDocker is already installed: {current_version}")
        if verify_docker_installation():
            print("Docker is working correctly.")
            return
        else:
            print("Docker is installed but may not be working correctly.")
            print("Please ensure Docker Desktop is running and try again.")
            return
    
    print(lang.get("installing_docker_windows", "Installing Docker on Windows..."))
    print(lang.get("docker_install_method_prompt", "\nChoose Docker installation method:"))
    print(lang.get("docker_install_method_choco", "1. Chocolatey (Recommended, requires admin CMD/PowerShell)"))
    print(lang.get("docker_install_method_manual", "2. Manual Download"))
    
    try:
        choice = int(input("Enter your choice (1-2): ").strip())
        
        if choice == 1:
            install_docker_chocolatey(lang)
        elif choice == 2:
            install_docker_manual(lang)
        else:
            print(lang.get("docker_install_invalid_choice", "Invalid choice. Please select 1 or 2."))
    
    except ValueError:
        print(lang.get("docker_install_invalid_input", "Invalid input. Please enter a number."))
    except Exception as e:
        print(f"An error occurred: {e}")

"""Windows manual Docker installation operations."""
from ...common.docker_utils import open_docker_download_page

def show_manual_install_instructions():
    """Display manual installation instructions for Docker Desktop."""
    print("\nPlease follow these steps to install Docker Desktop:")
    print("1. Open your web browser and go to: https://www.docker.com/products/docker-desktop")
    print("2. Click 'Download for Windows'")
    print("3. Once downloaded, run the installer")
    print("4. Follow the installation wizard:")
    print("   - Ensure 'Use WSL 2 instead of Hyper-V' is selected")
    print("   - Check 'Add shortcut to desktop'")
    print("5. Restart your computer after installation")
    print("\nAfter installation, verify Docker is working:")
    print("1. Open Command Prompt or PowerShell")
    print("2. Run: docker --version")
    print("3. Run: docker run hello-world")

def install_docker_manual(lang):
    """
    Guide the user through manual Docker installation.
    
    Args:
        lang (dict): Language translations
        
    Returns:
        bool: True if process was started, False if user declined
    """
    show_manual_install_instructions()
    
    # Offer to open the download page
    open_browser = input("\nWould you like me to open the Docker Desktop download page? (y/n): ").lower().strip()
    if open_browser == 'y':
        if not open_docker_download_page():
            print("Could not automatically open the browser. Please visit https://www.docker.com/products/docker-desktop manually.")
            return False
        return True
    
    return False

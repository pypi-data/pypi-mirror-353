import subprocess
import os

def install_docker_linux(lang):
    """
    Install Docker on Linux systems.
    
    Args:
        lang (dict): Language translations
    """
    print(lang.get("installing_docker_linux", "Installing Docker on Linux..."))
    
    try:
        # Update package list
        subprocess.run(["sudo", "apt-get", "update"], check=True)
        
        # Install Docker
        subprocess.run(["sudo", "apt-get", "install", "docker.io", "-y"], check=True)
        
        # Start and enable Docker service
        subprocess.run(["sudo", "systemctl", "start", "docker"], check=True)
        subprocess.run(["sudo", "systemctl", "enable", "docker"], check=True)
        
        # Add current user to docker group to avoid using sudo
        current_user = os.getlogin()
        subprocess.run(["sudo", "usermod", "-aG", "docker", current_user], check=True)
        
        print(lang.get("docker_install_success_linux", "Docker has been successfully installed."))
        print(lang.get("docker_verify_linux", "Verify installation by running: docker --version"))
    
    except subprocess.CalledProcessError as e:
        print(lang.get("docker_install_error_linux", f"Error installing Docker: {e}"))
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

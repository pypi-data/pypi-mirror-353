"""Common Docker utility functions."""
import subprocess
import webbrowser

def verify_docker_installation():
    """
    Verify Docker installation by running basic commands.
    
    Returns:
        bool: True if Docker is properly installed, False otherwise
    """
    try:
        # Check Docker version
        version_check = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if version_check.returncode != 0:
            return False
        
        # Try running hello-world container
        hello_check = subprocess.run(["docker", "run", "hello-world"], capture_output=True, text=True)
        return hello_check.returncode == 0
    except Exception:
        return False

def open_docker_download_page():
    """
    Open the Docker Desktop download page in the default web browser.
    
    Returns:
        bool: True if browser opened successfully, False otherwise
    """
    try:
        return webbrowser.open("https://www.docker.com/products/docker-desktop")
    except Exception:
        return False

def get_docker_version():
    """
    Get the installed Docker version.
    
    Returns:
        str: Docker version string or None if not installed
    """
    try:
        result = subprocess.run(["docker", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            return result.stdout.strip()
        return None
    except Exception:
        return None

"""Docker-related CLI operations."""
import platform
from .platforms.common.docker_utils import verify_docker_installation, get_docker_version

def install_docker(lang):
    """
    Install Docker on the current system.
    
    Args:
        lang (dict): Language translations
    """
    system = platform.system()
    
    try:
        # Check if Docker is already installed and working
        current_version = get_docker_version()
        if current_version:
            print(f"\nDocker is already installed: {current_version}")
            if verify_docker_installation():
                print("Docker is working correctly.")
                return
            else:
                print("Docker is installed but may not be working correctly.")
                print("Please ensure Docker service is running and try again.")
                return
        
        # Import and run platform-specific installation
        if system == "Windows":
            from .platforms.windows.docker_install import install_docker_windows
            install_docker_windows(lang)
        elif system == "Linux":
            from .platforms.linux.docker_install import install_docker_linux
            install_docker_linux(lang)
        elif system == "Darwin":  # macOS
            from .platforms.mac.docker_install import install_docker_mac
            install_docker_mac(lang)
        else:
            print(lang.get("unsupported_os", f"Docker installation is not supported on {system}"))
    except Exception as e:
        print(f"Failed to install Docker: {e}")

def uninstall_docker(lang):
    """
    Uninstall Docker from the current system.
    
    Args:
        lang (dict): Language translations
    """
    system = platform.system()
    
    try:
        # Import and run platform-specific uninstallation
        if system == "Windows":
            from .platforms.windows.docker_install import uninstall_docker_windows
            uninstall_docker_windows(lang)
        elif system == "Linux":
            from .platforms.linux.docker_install import uninstall_docker_linux
            uninstall_docker_linux(lang)
        elif system == "Darwin":  # macOS
            from .platforms.mac.docker_install import uninstall_docker_mac
            uninstall_docker_mac(lang)
        else:
            print(lang.get("unsupported_os", f"Docker uninstallation is not supported on {system}"))
    except Exception as e:
        print(f"Failed to uninstall Docker: {e}")

def check_docker_installed():
    """
    Check if Docker is installed and running.
    
    Returns:
        bool: True if Docker is installed and running, False otherwise
    """
    try:
        # First, check if docker module is available
        import docker
        DOCKER_AVAILABLE = True
    except ImportError:
        DOCKER_AVAILABLE = False
    
    if not DOCKER_AVAILABLE:
        return False
    
    try:
        # Try to create a Docker client
        client = docker.from_env()
        
        # Check if Docker daemon is running
        client.ping()
        return True
    except Exception:
        return False

def open_admin_cmd_and_install_docker():
    """
    Attempt to open an admin Command Prompt and run Docker installation.
    
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        import ctypes
        import os
        import sys
        
        # Check if running as admin
        def is_admin():
            try:
                return ctypes.windll.shell32.IsUserAnAdmin()
            except:
                return False
        
        # If not admin, use ShellExecute to run as admin
        if not is_admin():
            # Get the full path to the current Python interpreter
            python_exe = sys.executable
            
            # Get the full path to the current script
            script_path = os.path.abspath(sys.argv[0])
            
            # Construct the command to run Chocolatey Docker installation
            cmd = f'choco install docker-desktop -y'
            
            # Use ShellExecute to run the command in an elevated CMD
            try:
                ctypes.windll.shell32.ShellExecuteW(
                    None, 
                    "runas", 
                    "cmd.exe", 
                    f"/c {cmd}", 
                    None, 
                    1
                )
                return True
            except Exception as e:
                print(f"Failed to open admin CMD: {e}")
                return False
        
        return False
    except Exception as e:
        print(f"An error occurred while trying to open admin CMD: {e}")
        return False

def create_database_container(db_type, container_name=None):
    """
    Create a database container.
    
    Args:
        db_type (str): Type of database (e.g., 'mariadb')
        container_name (str, optional): Name for the container. Defaults to None.
    
    Returns:
        dict: Container creation result
    """
    # Validate Docker is installed and running
    if not check_docker_installed():
        return {
            "success": False,
            "error": "Docker is not installed or not running. Please install Docker first."
        }
    
    # Generate a unique container name if not provided
    if not container_name:
        container_name = f"easedb_{db_type}_{str(uuid.uuid4())[:8]}"
    
    try:
        # Create Docker client
        import docker
        client = docker.from_env()
        
        # Mapping database types to Docker images
        db_images = {
            "mariadb": "mariadb:latest",
            "mysql": "mysql:latest",
            "postgres": "postgres:latest"
        }
        
        # Validate database type
        if db_type.lower() not in db_images:
            return {
                "success": False,
                "error": f"Unsupported database type: {db_type}"
            }
        
        # Pull the image
        image = db_images[db_type.lower()]
        client.images.pull(image)
        
        # Create container
        container = client.containers.run(
            image,
            name=container_name,
            detach=True,
            environment={
                "MYSQL_ALLOW_EMPTY_PASSWORD": "yes"  # For MariaDB/MySQL
            }
        )
        
        return {
            "success": True,
            "container_id": container.id,
            "container_name": container_name
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }

def list_database_containers():
    """
    List all database containers.
    
    Returns:
        list: List of database containers
    """
    if not check_docker_installed():
        return []
    
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list()
        return [
            {
                "id": container.id,
                "name": container.name,
                "status": container.status
            } for container in containers
        ]
    except Exception:
        return []

def setup_database(db_type, lang):
    """Set up a new database using Docker."""
    result = create_database_container(db_type)
    if result["success"]:
        print(f"Database container '{result['container_name']}' created successfully.")
    else:
        print(result["error"])

def start_container(lang):
    """Start a database container."""
    containers = list_database_containers()
    if not containers:
        print("No containers found.")
        return
    
    print("Select a container to start:")
    for i, container in enumerate(containers):
        print(f"{i+1}. {container['name']} ({container['id']})")
    
    choice = input("Enter the container number: ")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(containers):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input.")
        return
    
    container = containers[choice-1]
    try:
        import docker
        client = docker.from_env()
        client.containers.start(container["id"])
        print(f"Container '{container['name']}' started successfully.")
    except Exception as e:
        print(f"Failed to start container: {e}")

def stop_container(lang):
    """Stop a running database container."""
    containers = list_database_containers()
    if not containers:
        print("No containers found.")
        return
    
    print("Select a container to stop:")
    for i, container in enumerate(containers):
        print(f"{i+1}. {container['name']} ({container['id']})")
    
    choice = input("Enter the container number: ")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(containers):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input.")
        return
    
    container = containers[choice-1]
    try:
        import docker
        client = docker.from_env()
        client.containers.stop(container["id"])
        print(f"Container '{container['name']}' stopped successfully.")
    except Exception as e:
        print(f"Failed to stop container: {e}")

def delete_container(lang):
    """Delete a database container."""
    containers = list_database_containers()
    if not containers:
        print("No containers found.")
        return
    
    print("Select a container to delete:")
    for i, container in enumerate(containers):
        print(f"{i+1}. {container['name']} ({container['id']})")
    
    choice = input("Enter the container number: ")
    try:
        choice = int(choice)
        if choice < 1 or choice > len(containers):
            print("Invalid choice.")
            return
    except ValueError:
        print("Invalid input.")
        return
    
    container = containers[choice-1]
    try:
        import docker
        client = docker.from_env()
        client.containers.remove(container["id"], force=True)
        print(f"Container '{container['name']}' deleted successfully.")
    except Exception as e:
        print(f"Failed to delete container: {e}")

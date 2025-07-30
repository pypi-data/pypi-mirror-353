from .docker import (
    check_docker_installed, 
    install_docker, 
    uninstall_docker,
    create_database_container, 
    start_container, 
    stop_container, 
    delete_container
)
from .utils import load_language

def execute_command(choice, lang):
    """
    Execute a command based on user's choice.
    
    Args:
        choice (int): User's menu selection
        lang (dict): Language translations
    """
    if choice == 1:
        create_database(lang)
    elif choice == 2:
        start_database(lang)
    elif choice == 3:
        stop_database(lang)
    elif choice == 4:
        delete_database(lang)
    elif choice == 5:
        install_docker_wrapper(lang)
    elif choice == 6:
        uninstall_docker_wrapper(lang)
    elif choice == 7:
        print(lang["goodbye"])
        exit(0)
    else:
        print(lang["invalid_option"])

def create_database(lang):
    """
    Create a new database.
    
    Args:
        lang (dict): Language translations
    """
    # Check Docker installation first
    if not check_docker_installed():
        print(lang.get("docker_not_installed", "Docker is not installed. Please install it first."))
        install_choice = input(f"Would you like to install Docker? (y/n): ").lower().strip()
        if install_choice == 'y':
            install_docker(lang)
        return

    print(lang["choose_database_type"])
    db_type = input().lower()
    
    db_name = input(lang["enter_db_name"])
    
    # Attempt to create database container
    result = create_database_container(db_type, db_name)
    
    if result["success"]:
        print(lang["database_created"].format(name=result["container_name"]))
    else:
        print(lang["error_creating_database"].format(error=result["error"]))

def start_database(lang):
    """
    Start an existing database.
    
    Args:
        lang (dict): Language translations
    """
    # Check Docker installation first
    if not check_docker_installed():
        print(lang.get("docker_not_installed", "Docker is not installed. Please install it first."))
        return
    
    start_container(lang)

def stop_database(lang):
    """
    Stop a running database.
    
    Args:
        lang (dict): Language translations
    """
    # Check Docker installation first
    if not check_docker_installed():
        print(lang.get("docker_not_installed", "Docker is not installed. Please install it first."))
        return
    
    stop_container(lang)

def delete_database(lang):
    """
    Delete a database container.
    
    Args:
        lang (dict): Language translations
    """
    # Check Docker installation first
    if not check_docker_installed():
        print(lang.get("docker_not_installed", "Docker is not installed. Please install it first."))
        return
    
    delete_container(lang)

def install_docker_wrapper(lang):
    """
    Wrapper for Docker installation.
    
    Args:
        lang (dict): Language translations
    """
    if not check_docker_installed():
        install_docker(lang)
    else:
        print("Docker is already installed.")

def uninstall_docker_wrapper(lang):
    """
    Wrapper for Docker uninstallation.
    
    Args:
        lang (dict): Language translations
    """
    if check_docker_installed():
        confirm = input("Are you sure you want to uninstall Docker? This will remove all Docker containers. (y/n): ").lower().strip()
        if confirm == 'y':
            uninstall_docker(lang)
        else:
            print("Docker uninstallation cancelled.")
    else:
        print("Docker is not currently installed.")

def run_cli_menu(lang):
    """
    Run the main CLI menu.
    
    Args:
        lang (dict): Language translations
    """
    while True:
        print("\n=== " + lang.get("title", "EaseDB CLI") + " ===")
        print("1. " + lang["create_database"])
        print("2. " + lang["start_database"])
        print("3. " + lang["stop_database"])
        print("4. " + lang["delete_database"])
        print("5. " + lang["install_docker"])
        print("6. Uninstall Docker")
        print("7. " + lang["exit"])
        
        try:
            choice = input(lang["choose_option"])
            if choice.isdigit():
                execute_command(int(choice), lang)
            else:
                print(lang["invalid_option"])
        except KeyboardInterrupt:
            print("\n" + lang["goodbye"])
            break

import subprocess
import webbrowser

def install_docker_mac(lang):
    """
    Install Docker on macOS.
    
    Args:
        lang (dict): Language translations
    """
    print(lang.get("installing_docker_mac", "Installing Docker on macOS..."))
    print(lang.get("docker_install_method_prompt_mac", "\nChoose Docker installation method:"))
    print(lang.get("docker_install_method_homebrew", "1. Homebrew (Recommended)"))
    print(lang.get("docker_install_method_manual_mac", "2. Manual Download (Docker Desktop)"))
    
    try:
        choice = int(input("Enter your choice (1-2): ").strip())
        
        if choice == 1:
            # Homebrew Docker installation
            try:
                # Check if Homebrew is installed
                subprocess.run(["brew", "--version"], capture_output=True, check=True)
                
                # Install Docker
                subprocess.run(["brew", "install", "docker"], check=True)
                
                print(lang.get("docker_install_success_homebrew", "Docker installed successfully via Homebrew."))
                print(lang.get("docker_verify_command", "Verify installation by running: docker --version"))
            
            except subprocess.CalledProcessError:
                print(lang.get("homebrew_not_found", "Homebrew not found. Please install Homebrew first."))
                print("Visit https://brew.sh/ to install Homebrew.")
        
        elif choice == 2:
            # Manual Docker Desktop download
            print("\nPlease follow these steps to install Docker Desktop:")
            print("1. Open your web browser and go to: https://www.docker.com/products/docker-desktop")
            print("2. Click 'Download for Mac'")
            print("3. Once downloaded, open the .dmg file")
            print("4. Drag Docker Desktop to your Applications folder")
            print("5. Launch Docker Desktop and follow the installation wizard")
            
            # Offer to open the download page
            open_browser = input("\nWould you like me to open the Docker Desktop download page? (y/n): ").lower().strip()
            if open_browser == 'y':
                try:
                    webbrowser.open("https://www.docker.com/products/docker-desktop")
                except Exception:
                    print("Could not automatically open the browser. Please visit https://www.docker.com/products/docker-desktop manually.")
        
        else:
            print(lang.get("docker_install_invalid_choice", "Invalid choice. Please select 1 or 2."))
    
    except ValueError:
        print(lang.get("docker_install_invalid_input", "Invalid input. Please enter a number."))
    except Exception as e:
        print(f"An error occurred: {e}")

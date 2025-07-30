"""Windows-specific Docker operations."""
from .chocolatey import install_docker_chocolatey
from .manual import install_docker_manual
from .uninstall import uninstall_docker_windows

__all__ = [
    'install_docker_chocolatey',
    'install_docker_manual',
    'uninstall_docker_windows'
]

from pathlib import Path
from urllib.parse import urlparse, unquote
import os, platform, sys

def get_absolute_path(relative_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)


def uri_to_path(uri: str) -> Path:
    """Converts a URI to a Path object, with handling for Windows paths."""
    path = urlparse(uri).path
    path = unquote(path)

    # If running on Windows and the path contains a colon (drive letter), remove the leading '/'
    if ':' in path:
        path = path.lstrip('/')

    return Path(path)

"""

def get_wuff_lib_filename():
    # Base filename for the library
    base_filename = "wuff"

    # Determine OS and architecture
    os_system = platform.system().lower()
    arch = platform.machine().lower()

    # Normalize architecture names
    if arch in ["x86_64", "amd64"]:
        arch = "x64"
    elif arch in ["arm64"]:
        arch = "arm64"
    else:
        raise ValueError("Unsupported architecture: {}".format(arch))

    # Construct the filename based on OS and architecture
    if os_system == "windows":
        filename = "{}-{}-{}.dll".format(base_filename, os_system, arch)
    elif os_system == "linux":
        filename = "{}-{}-{}.so".format(base_filename, os_system, arch)
    elif os_system == "darwin":  # macOS
        filename = "{}-{}-{}.dylib".format(base_filename, os_system, arch)
    else:
        raise ValueError("Unsupported operating system: {}".format(os_system))

    return filename



def load_wuff_library():
    lib_filename = get_wuff_lib_filename()

    lib_path = os.path.join(os.path.dirname(__file__), 'lib', lib_filename)

    # Add the library's directory to sys.path if not already present
    if os.path.dirname(lib_path) not in sys.path:
        sys.path.append(os.path.dirname(lib_path))

    # Import the module
    from Wuff import *
"""

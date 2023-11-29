from pathlib import Path
from urllib.parse import urlparse, unquote
import os

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

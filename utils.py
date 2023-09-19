from pathlib import Path
from urllib.parse import urlparse
import os

def get_absolute_path(relative_path):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, relative_path)

def uri_to_path(uri: str) -> Path:
    """Converts a URI to a Path object."""
    return Path(urlparse(uri).path)
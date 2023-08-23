from pathlib import Path
from urllib.parse import urlparse

def uri_to_path(uri: str) -> Path:
    """Converts a URI to a Path object."""
    return Path(urlparse(uri).path)
import os
import platform
from pathlib import Path
from typing import Union, List, Tuple
import ctypes
import re

PathString = Union[str, Path]

# Windows API constants
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF
FILE_ATTRIBUTE_HIDDEN = 0x2


def is_windows_os() -> bool:
    """Check if the program is running on Windows."""
    return platform.system() == 'Windows'


def validate_windows_path(path: PathString) -> Tuple[bool, str]:
    """
    Validate a Windows path for correctness.

    Checks:
    - Existence of the path (file or directory must exist).
    - No prohibited characters in any path component except the drive letter.
      Prohibited characters: < > : " | ? * (colon is only allowed as drive letter).
    - Total path length <= 260 characters (standard Windows limit).

    Returns:
        Tuple[bool, str]: (True, '') if valid, else (False, error message).
    """
    path_obj = Path(path)
    path_str = str(path_obj)

    # 1. Check existence
    if not path_obj.exists():
        return False, 'Path does not exist.'

    # 2. Check for prohibited characters in each path component (excluding drive)
    #    Drive letter (e.g. "C:") is allowed; colon elsewhere is prohibited.
    drive = path_obj.drive  # e.g. "C:" or ""
    parts = path_obj.parts

    # Allowed colon only in drive part
    if drive:
        # Validate drive format: single letter + colon, optionally followed by separator
        if not re.match(r'^[a-zA-Z]:[\\/]?$', drive):
            return False, f'Invalid drive specification: {drive}'
        # Remove drive from the list of parts to validate separately
        other_parts = parts[1:] if len(parts) > 1 else []
    else:
        other_parts = parts

    # Prohibited characters in file/directory names (Windows)
    # Note: forward slash '/' is a valid separator and will be normalized by Path,
    #       so we do not treat it as an invalid character here.
    invalid_chars_pattern = r'[<>:"|?*]'  # double quote, colon, pipe, question, star, etc.
    for part in other_parts:
        if re.search(invalid_chars_pattern, part):
            return False, f'Prohibited character(s) in "{part}".'
        # Control characters (0-31) are also invalid
        if any(ord(c) < 32 for c in part):
            return False, f'Control character in "{part}".'

    # 3. Check total path length (max 260 characters)
    if len(path_str) >= 260:
        return False, 'Path length exceeds 260 characters.'

    return True, ''


def format_size(size_bytes: int) -> str:
    """
    Convert file size in bytes to a human-readable string (Windows style).

    Uses binary units: KB = 1024, MB = 1024**2, GB = 1024**3.
    Examples:
        1024 -> '1.0 KB'
        1500000 -> '1.4 MB'
    """
    if size_bytes < 1024:
        return f'{size_bytes} B'
    if size_bytes < 1024 ** 2:
        return f'{size_bytes / 1024:.1f} KB'
    if size_bytes < 1024 ** 3:
        return f'{size_bytes / 1024 ** 2:.1f} MB'
    return f'{size_bytes / 1024 ** 3:.1f} GB'


def get_parent_path(path: PathString) -> str:
    """
    Return the parent directory of the given path, with Windows‑specific handling.

    For root directories (e.g. 'C:\\') the parent is the same directory.
    For relative paths, returns '.' if no meaningful parent exists.
    If an error occurs, returns an empty string.
    """
    try:
        path_obj = Path(path)
        parent = path_obj.parent
        parent_str = str(parent)

        # Path('.').parent returns '.' – keep it as is
        return parent_str
    except Exception:
        # Return empty string on any unexpected error (e.g. malformed path)
        return ''


def safe_windows_listdir(path: PathString) -> List[str]:
    """
    Safely list the contents of a directory on Windows.

    Returns a list of full paths of all items in the directory.
    On any error (permission, not found, path too long, etc.) returns an empty list.
    """
    path_obj = Path(path)
    try:
        # iterdir() yields Path objects; convert each to string (full path)
        return [str(child) for child in path_obj.iterdir()]
    except (PermissionError, FileNotFoundError, OSError):
        # All expected Windows directory listing errors -> empty list
        return []


def is_hidden_windows_file(path: PathString) -> bool:
    """
    Check if a file or directory has the 'hidden' attribute set on Windows.

    Uses GetFileAttributesW from kernel32.dll. Returns False if the file does
    not exist, if the function fails, or if running on a non‑Windows platform.
    Raises OSError if called on a non‑Windows system.
    """
    if not is_windows_os():
        raise OSError('This function is only available on Windows.')

    path_str = str(path)

    # Retrieve file attributes
    attrs = ctypes.windll.kernel32.GetFileAttributesW(path_str)

    # Failure: file does not exist, access denied, etc.
    if attrs == INVALID_FILE_ATTRIBUTES:
        return False

    # Check the hidden attribute bit (0x2)
    return bool(attrs & FILE_ATTRIBUTE_HIDDEN)
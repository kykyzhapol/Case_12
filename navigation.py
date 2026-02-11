"""
Windows file system navigation utilities.
Provides functions for drive listing, directory navigation, and folder information retrieval.
"""

import os
from datetime import datetime
from typing import List, Dict, Any, Tuple
from pathlib import Path

import utils  # Custom utilities for Windows file operations


def get_current_drive() -> str:
    """
    Get the current Windows drive where the script is located.

    Returns:
        str: Drive letter with colon (e.g., 'C:') or empty string if no drive.
    """
    path = os.path.abspath(__file__)
    drive, _ = os.path.splitdrive(path)
    return drive


def list_available_drives() -> List[str]:
    """
    List all available drives on Windows system.

    Returns:
        List[str]: List of drive letters with colon (e.g., ['C:', 'D:', 'E:']).

    Raises:
        NotImplementedError: On non-Windows platforms.
    """
    if not utils.is_windows_os():
        raise NotImplementedError('This function is only available on Windows.')

    drives = []
    # Check drive letters from A: to Z:
    for letter in range(ord('A'), ord('Z') + 1):
        drive = f'{chr(letter)}:'
        # Use GetDriveTypeW to check if drive exists and is available
        if ctypes.windll.kernel32.GetDriveTypeW(drive) != 1:  # 1 = DRIVE_NO_ROOT_DIR
            drives.append(drive)

    return drives


def list_directory(path: str) -> Tuple[bool, List[Dict[str, Any]]]:
    """
    List contents of a directory with detailed file information.

    Args:
        path (str): Directory path to list.

    Returns:
        Tuple[bool, List[Dict[str, Any]]]: 
            (True, list of file information dictionaries) on success,
            (False, []) on failure.
            Each dictionary contains:
                - 'name': str - Full filename with extension
                - 'type': str - 'file' or 'dir'
                - 'size': int - Size in bytes (0 for directories)
                - 'modified': str - Last modified date in YYYY-MM-DD format
                - 'hidden': bool - Whether file is hidden
    """
    try:
        # Get all items in the directory
        items_paths = utils.safe_windows_listdir(path)

        if not isinstance(items_paths, list):
            # Handle case when safe_windows_listdir returns non-list (shouldn't happen now)
            return False, []

        items_info = []

        for item_path_str in items_paths:
            try:
                item_path = Path(item_path_str)

                # Get basic file info
                name = item_path.name
                is_dir = item_path.is_dir()

                # Get file size (0 for directories)
                size = 0 if is_dir else item_path.stat().st_size

                # Get modification date
                mtime = item_path.stat().st_mtime
                modified = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')

                # Check if hidden (Windows only)
                hidden = False
                if utils.is_windows_os():
                    hidden = utils.is_hidden_windows_file(str(item_path))

                item_info = {
                    'name': name,
                    'type': 'dir' if is_dir else 'file',
                    'size': size,
                    'modified': modified,
                    'hidden': hidden,
                    'path': str(item_path)  # Full path for navigation
                }
                items_info.append(item_info)

            except (PermissionError, OSError, FileNotFoundError):
                # Skip items that can't be accessed
                continue

        # Sort directories first, then files, alphabetically
        items_info.sort(key=lambda x: (x['type'] != 'dir', x['name'].lower()))

        return True, items_info

    except Exception:
        return False, []


def format_directory_output(items: List[Dict[str, Any]]) -> None:
    """
    Pretty-print directory contents with Windows-specific formatting.

    Args:
        items (List[Dict[str, Any]]): List of file info dictionaries from list_directory().
    """
    if not items:
        print("Directory is empty or cannot be accessed.")
        return

    # Separate hidden and non-hidden items
    normal_items = [item for item in items if not item['hidden']]
    hidden_items = [item for item in items if item['hidden']]

    # Print headers
    print(f"\n{'Name':<40} {'Type':<8} {'Size':>12} {'Modified':<12} {'Attributes':<10}")
    print('-' * 85)

    # Print normal items
    for item in normal_items:
        name = item['name'][:37] + '...' if len(item['name']) > 40 else item['name']
        size_str = utils.format_size(item['size']) if item['type'] == 'file' else '<DIR>'
        modified = item['modified']
        attrs = 'H' if item['hidden'] else ''

        print(f"{name:<40} {item['type']:<8} {size_str:>12} {modified:<12} {attrs:<10}")

    # Print hidden items if any
    if hidden_items:
        print("\nHidden items:")
        for item in hidden_items:
            name = item['name'][:37] + '...' if len(item['name']) > 40 else item['name']
            size_str = utils.format_size(item['size']) if item['type'] == 'file' else '<DIR>'
            print(f"  {name:<38} {item['type']:<8} {size_str:>12}")


def move_up(current_path: str) -> str:
    """
    Navigate to the parent directory.

    Args:
        current_path (str): Current directory path.

    Returns:
        str: Parent directory path if valid, otherwise current_path.
    """
    if not current_path:
        return ''

    parent_path = utils.get_parent_path(current_path)

    # If we're at root, stay at root
    if parent_path == current_path:
        return parent_path

    # Validate the parent path
    is_valid, _ = utils.validate_windows_path(parent_path)

    if is_valid:
        return parent_path

    # If parent is invalid, try to stay in current directory
    is_current_valid, _ = utils.validate_windows_path(current_path)
    return current_path if is_current_valid else ''


def move_down(current_path: str, target_dir: str) -> Tuple[bool, str]:
    """
    Navigate into a subdirectory.

    Args:
        current_path (str): Current directory path.
        target_dir (str): Name of the target subdirectory.

    Returns:
        Tuple[bool, str]: (True, new_path) on success, (False, current_path) on failure.
    """
    # Sanitize input
    target_dir = target_dir.strip('\\/ ')
    if not target_dir:
        return False, current_path

    # Construct new path
    new_path = os.path.join(current_path, target_dir)

    # Check if target exists and is a directory
    try:
        if Path(new_path).is_dir():
            # Validate the new path
            is_valid, _ = utils.validate_windows_path(new_path)
            if is_valid:
                return True, new_path
    except (PermissionError, OSError):
        pass

    return False, current_path


def get_windows_special_folders() -> Dict[str, str]:
    """
    Get paths to Windows special folders.

    Returns:
        Dict[str, str]: Dictionary mapping folder names to their full paths.
                        Includes Desktop, Documents, Downloads, and common profile folders.
    """
    special_folders = {}

    # Get user profile directory
    user_profile = os.environ.get('USERPROFILE', '')
    if not user_profile:
        return special_folders

    # Known special folders
    known_folders = {
        'Desktop': 'Desktop',
        'Documents': 'Documents',
        'Downloads': 'Downloads',
        'Pictures': 'Pictures',
        'Music': 'Music',
        'Videos': 'Videos'
    }

    # Add folders that exist
    for display_name, folder_name in known_folders.items():
        folder_path = os.path.join(user_profile, folder_name)
        if Path(folder_path).exists():
            special_folders[display_name] = folder_path

    # Try to get OneDrive folder if available
    onedrive = os.environ.get('OneDrive', '')
    if onedrive and Path(onedrive).exists():
        special_folders['OneDrive'] = onedrive

    # Add common system folders using CSIDL/SHGetFolderPath if needed
    # This could be extended with SHGetKnownFolderPath for more accuracy

    return special_folders
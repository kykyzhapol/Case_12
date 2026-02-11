"""
Windows file system analysis module.
Provides recursive file counting, size calculation, type statistics, and attribute analysis.
"""

import os
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from pathlib import Path
import ctypes

import utils
import navigation

# Windows file attribute constants
FILE_ATTRIBUTE_READONLY = 0x1
FILE_ATTRIBUTE_HIDDEN = 0x2
FILE_ATTRIBUTE_SYSTEM = 0x4
FILE_ATTRIBUTE_DIRECTORY = 0x10
INVALID_FILE_ATTRIBUTES = 0xFFFFFFFF


def count_files(path: str) -> Tuple[bool, int]:
    """
    Recursively count files in a Windows directory.

    Args:
        path (str): Directory path to analyze.

    Returns:
        Tuple[bool, int]: (True, file_count) on success, (False, 0) on failure.
    """
    try:
        # Get directory contents
        dir_contents = utils.safe_windows_listdir(path)
        if not isinstance(dir_contents, list):
            return False, 0

        success, items = navigation.list_directory(path)
        if not success or not items:
            return False, 0

        file_count = 0

        for item in items:
            # Construct full path correctly
            full_path = os.path.join(path, item['name'])

            if item['type'] == 'dir':
                # Recursively count files in subdirectory
                sub_success, sub_count = count_files(full_path)
                if sub_success:
                    file_count += sub_count
                # Continue even if subdirectory fails (permission issues)
            else:  # File
                file_count += 1

        return True, file_count

    except (PermissionError, FileNotFoundError, OSError):
        return False, 0
    except Exception:
        return False, 0


def count_bytes(path: str) -> Tuple[bool, int]:
    """
    Recursively calculate total size of all files in a Windows directory.

    Args:
        path (str): Directory path to analyze.

    Returns:
        Tuple[bool, int]: (True, total_bytes) on success, (False, 0) on failure.
    """
    try:
        dir_contents = utils.safe_windows_listdir(path)
        if not isinstance(dir_contents, list):
            return False, 0

        success, items = navigation.list_directory(path)
        if not success or not items:
            return False, 0

        total_size = 0

        for item in items:
            full_path = os.path.join(path, item['name'])

            if item['type'] == 'dir':
                # Skip junction points and symlinks to avoid infinite recursion
                try:
                    if os.path.islink(full_path):
                        continue
                except (OSError, AttributeError):
                    # islink might not be available on some Windows Python versions
                    pass

                # Recursively count bytes in subdirectory
                sub_success, sub_size = count_bytes(full_path)
                if sub_success:
                    total_size += sub_size
            else:  # File
                total_size += item['size']

        return True, total_size

    except (PermissionError, FileNotFoundError, OSError):
        return False, 0
    except Exception:
        return False, 0


def analyze_windows_file_types(path: str) -> Tuple[bool, Dict[str, Dict[str, Any]]]:
    """
    Analyze file types (extensions) in a directory and all subdirectories.

    Args:
        path (str): Directory path to analyze.

    Returns:
        Tuple[bool, Dict[str, Dict[str, Any]]]: 
            (True, stats_dict) on success, (False, {}) on failure.
            stats_dict format: {'.ext': {'count': int, 'size': int, 'ext': str}}
    """
    try:
        success, items = navigation.list_directory(path)
        if not success or not items:
            return False, {}

        # Dictionary for aggregation: {'.ext': {'count': 0, 'size': 0}}
        stats = defaultdict(lambda: {'count': 0, 'size': 0, 'ext': ''})

        for item in items:
            full_path = os.path.join(path, item['name'])

            if item['type'] == 'dir':
                # Skip junction points and symlinks
                try:
                    if os.path.islink(full_path):
                        continue
                except (OSError, AttributeError):
                    pass

                # Recursively analyze subdirectory
                sub_success, sub_stats = analyze_windows_file_types(full_path)
                if sub_success:
                    for ext, sub_data in sub_stats.items():
                        stats[ext]['count'] += sub_data['count']
                        stats[ext]['size'] += sub_data['size']
                        stats[ext]['ext'] = ext
            else:  # File
                # Extract file extension
                name = item['name']
                _, ext = os.path.splitext(name)

                # Normalize extension: lowercase with dot
                if ext:
                    ext = ext.lower()
                else:
                    ext = '(no extension)'

                stats[ext]['count'] += 1
                stats[ext]['size'] += item['size']
                stats[ext]['ext'] = ext

        return True, dict(stats)

    except (PermissionError, FileNotFoundError, OSError):
        return False, {}
    except Exception:
        return False, {}


def get_windows_file_attributes_stats(path: str) -> Dict[str, int]:
    """
    Recursively collect statistics about Windows file attributes.

    Args:
        path (str): Directory path to analyze.

    Returns:
        Dict[str, int]: Dictionary with counts of 'hidden', 'system', 'readonly' files.
    """
    # Initialize stats dictionary
    stats = {'hidden': 0, 'system': 0, 'readonly': 0}

    # Check if running on Windows
    if not utils.is_windows_os():
        return stats

    try:
        success, items = navigation.list_directory(path)
        if not success or not items:
            return stats

        for item in items:
            full_path = os.path.join(path, item['name'])

            try:
                if item['type'] == 'dir':
                    # Skip junction points and symlinks
                    if os.path.islink(full_path):
                        continue

                    # Recursively get stats from subdirectory
                    sub_stats = get_windows_file_attributes_stats(full_path)
                    for key in stats:
                        stats[key] += sub_stats[key]

                else:  # File
                    # Check hidden attribute
                    if item['hidden']:
                        stats['hidden'] += 1

                    # Get file attributes via ctypes for additional attributes
                    # First check if path exists and is accessible
                    if not os.path.exists(full_path):
                        continue

                    attrs = ctypes.windll.kernel32.GetFileAttributesW(full_path)

                    if attrs == INVALID_FILE_ATTRIBUTES:
                        continue

                    if attrs & FILE_ATTRIBUTE_SYSTEM:
                        stats['system'] += 1
                    if attrs & FILE_ATTRIBUTE_READONLY:
                        stats['readonly'] += 1

            except (PermissionError, OSError, AttributeError, FileNotFoundError):
                # Skip inaccessible files/directories
                continue

        return stats

    except Exception:
        return stats


def _get_largest_files(path: str, n: int = 5) -> List[Tuple[str, int]]:
    """
    Helper function to find the N largest files in a directory tree.

    Args:
        path (str): Directory path to analyze.
        n (int): Number of largest files to return.

    Returns:
        List[Tuple[str, int]]: List of (file_path, size_in_bytes) tuples, sorted by size descending.
    """
    try:
        files_with_size = []

        def collect_files(current_path: str) -> None:
            """Recursively collect all files with their sizes."""
            nonlocal files_with_size

            try:
                success, items = navigation.list_directory(current_path)
                if not success or not items:
                    return

                for item in items:
                    full_path = os.path.join(current_path, item['name'])

                    try:
                        if item['type'] == 'dir':
                            # Skip junction points and symlinks
                            if os.path.islink(full_path):
                                continue
                            collect_files(full_path)
                        else:  # File
                            files_with_size.append((full_path, item['size']))
                    except (PermissionError, OSError, FileNotFoundError):
                        continue

            except (PermissionError, FileNotFoundError, OSError):
                return

        collect_files(path)

        # Sort by size descending and take first n
        files_with_size.sort(key=lambda x: x[1], reverse=True)
        return files_with_size[:n]

    except Exception:
        return []


def show_windows_directory_stats(path: str) -> bool:
    """
    Display comprehensive statistics about a Windows directory.

    Args:
        path (str): Directory path to analyze.

    Returns:
        bool: True if analysis completed (even with partial data), False on critical failure.
    """
    try:
        print(f"\n{'=' * 60}")
        print(f"  DIRECTORY ANALYSIS: {path}")
        print(f"{'=' * 60}\n")

        # 1. Total file count
        print("[1/5] Counting files...")
        success, file_count = count_files(path)
        if success:
            print(f"    ✓ Total files: {file_count:,}")
        else:
            print("    ✗ Failed to count files (permission issues?)")

        # 2. Total size
        print("\n[2/5] Calculating total size...")
        success, total_bytes = count_bytes(path)
        if success:
            print(f"    ✓ Total size: {utils.format_size(total_bytes)}")
        else:
            print("    ✗ Failed to calculate total size")

        # 3. File type distribution
        print("\n[3/5] Analyzing file types...")
        success, file_types = analyze_windows_file_types(path)
        if success and file_types:
            print(f"    ✓ Found {len(file_types)} different file extensions")

            # Sort by count and show top 10
            sorted_types = sorted(
                file_types.items(),
                key=lambda x: x[1]['count'],
                reverse=True
            )[:10]

            print("\n    Top 10 file extensions by count:")
            print(f"    {'Extension':<20} {'Count':>10} {'Total Size':>15}")
            print(f"    {'-' * 20} {'-' * 10} {'-' * 15}")

            for ext, data in sorted_types:
                ext_display = ext if ext else '(no ext)'
                if len(ext_display) > 18:
                    ext_display = ext_display[:15] + '...'
                print(f"    {ext_display:<20} {data['count']:>10,} {utils.format_size(data['size']):>15}")
        else:
            print("    ✗ Failed to analyze file types")

        # 4. File attributes
        print("\n[4/5] Analyzing file attributes...")
        if utils.is_windows_os():
            attr_stats = get_windows_file_attributes_stats(path)
            print(f"    ✓ Hidden files: {attr_stats['hidden']:,}")
            print(f"    ✓ System files: {attr_stats['system']:,}")
            print(f"    ✓ Read-only files: {attr_stats['readonly']:,}")
        else:
            print("    ⚠ Attribute analysis only available on Windows")

        # 5. Largest files
        print("\n[5/5] Finding largest files...")
        largest = _get_largest_files(path, 5)
        if largest:
            print(f"    ✓ Found {len(largest)} largest files")

            print("\n    Largest files:")
            for i, (file_path, size) in enumerate(largest, 1):
                # Shorten path for display
                display_path = file_path
                if len(display_path) > 50:
                    display_path = '...' + display_path[-47:]
                print(f"    {i}. {display_path}")
                print(f"       Size: {utils.format_size(size)}")
        else:
            print("    ✗ Failed to find largest files")

        print(f"\n{'=' * 60}")
        print("  ANALYSIS COMPLETE")
        print(f"{'=' * 60}\n")

        return True

    except Exception as e:
        print(f"\n✗ Critical error during analysis: {e}")
        return False

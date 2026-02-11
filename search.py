"""
Windows file search module.
Provides various search functionalities: pattern matching, extension filtering, large file detection,
system file discovery, and interactive search menu.
"""

import os
import re
import fnmatch
from typing import List, Dict, Any, Tuple, Optional
from pathlib import Path

import utils
import navigation
import analysis


def find_files_windows(pattern: str, path: str, case_sensitive: bool = False) -> List[str]:
    """
    Search for files using Windows wildcard patterns (* and ?).

    Args:
        pattern (str): Search pattern (supports * and ? wildcards).
        path (str): Directory path to search in.
        case_sensitive (bool): If True, case-sensitive search; otherwise case-insensitive.

    Returns:
        List[str]: List of full paths to matching files.
    """
    matching_files = []

    # Convert Windows wildcards to regex pattern
    regex_pattern = fnmatch.translate(pattern)

    # Compile regex with appropriate case sensitivity
    flags = 0 if case_sensitive else re.IGNORECASE
    try:
        pattern_regex = re.compile(regex_pattern, flags)
    except re.error:
        # Fallback to simple containment if regex compilation fails
        pattern_lower = pattern.lower()

    def search_recursive(current_path: str) -> None:
        """Recursive search helper."""
        nonlocal matching_files

        try:
            success, items = navigation.list_directory(current_path)
            if not success or not items:
                return

            for item in items:
                full_path = os.path.join(current_path, item['name'])

                if item['type'] == 'dir':
                    # Skip junction points and symlinks
                    try:
                        if os.path.islink(full_path):
                            continue
                    except (OSError, AttributeError):
                        pass

                    # Recursively search subdirectory
                    search_recursive(full_path)
                else:  # File
                    # Check if file name matches pattern
                    try:
                        if 'pattern_regex' in locals():
                            if pattern_regex.match(item['name']):
                                matching_files.append(full_path)
                        else:
                            # Fallback matching
                            name_to_check = item['name'] if case_sensitive else item['name'].lower()
                            pattern_to_check = pattern if case_sensitive else pattern_lower
                            if pattern_to_check in name_to_check:
                                matching_files.append(full_path)
                    except (OSError, ValueError):
                        continue

        except (PermissionError, FileNotFoundError, OSError):
            return

    search_recursive(path)
    return matching_files


def find_by_windows_extension(extensions: List[str], path: str) -> List[str]:
    """
    Search for files by their extensions.

    Args:
        extensions (List[str]): List of extensions (with or without leading dot).
        path (str): Directory path to search in.

    Returns:
        List[str]: List of full paths to files with matching extensions.
    """
    # Normalize extensions: ensure they start with dot and are lowercase
    normalized_extensions = []
    for ext in extensions:
        ext = ext.strip().lower()
        if not ext.startswith('.'):
            ext = '.' + ext
        normalized_extensions.append(ext)

    matching_files = []

    def search_recursive(current_path: str) -> None:
        """Recursive search helper."""
        nonlocal matching_files

        try:
            success, items = navigation.list_directory(current_path)
            if not success or not items:
                return

            for item in items:
                full_path = os.path.join(current_path, item['name'])

                if item['type'] == 'dir':
                    # Skip junction points and symlinks
                    try:
                        if os.path.islink(full_path):
                            continue
                    except (OSError, AttributeError):
                        pass

                    search_recursive(full_path)
                else:  # File
                    # Get file extension
                    _, ext = os.path.splitext(item['name'])
                    if ext.lower() in normalized_extensions:
                        matching_files.append(full_path)

        except (PermissionError, FileNotFoundError, OSError):
            return

    search_recursive(path)
    return matching_files


def find_large_files_windows(min_size_mb: float, path: str) -> List[Dict[str, Any]]:
    """
    Find files larger than specified size.

    Args:
        min_size_mb (float): Minimum file size in megabytes.
        path (str): Directory path to search in.

    Returns:
        List[Dict[str, Any]]: List of dictionaries with file information:
            - 'path': Full file path
            - 'size_mb': File size in megabytes
            - 'size_bytes': File size in bytes
            - 'type': File extension
            - 'name': File name
    """
    min_size_bytes = int(min_size_mb * 1024 * 1024)
    large_files = []

    def search_recursive(current_path: str) -> None:
        """Recursive search helper."""
        nonlocal large_files

        try:
            success, items = navigation.list_directory(current_path)
            if not success or not items:
                return

            for item in items:
                full_path = os.path.join(current_path, item['name'])

                if item['type'] == 'dir':
                    # Skip junction points and symlinks
                    try:
                        if os.path.islink(full_path):
                            continue
                    except (OSError, AttributeError):
                        pass

                    search_recursive(full_path)
                else:  # File
                    if item['size'] >= min_size_bytes:
                        _, ext = os.path.splitext(item['name'])
                        large_files.append({
                            'path': full_path,
                            'size_mb': round(item['size'] / (1024 * 1024), 2),
                            'size_bytes': item['size'],
                            'type': ext.lower() if ext else '(no extension)',
                            'name': item['name']
                        })

        except (PermissionError, FileNotFoundError, OSError):
            return

    search_recursive(path)

    # Sort by size descending
    large_files.sort(key=lambda x: x['size_mb'], reverse=True)
    return large_files


def find_windows_system_files(path: Optional[str] = None) -> List[str]:
    """
    Find Windows system files (.exe, .dll, .sys) in system directories.

    Args:
        path (Optional[str]): If provided, search only in this path.
                             If None, search in standard Windows system directories.

    Returns:
        List[str]: List of full paths to system files.
    """
    system_files = []

    # If specific path is provided, search only there
    if path:
        return find_by_windows_extension(['.exe', '.dll', '.sys'], path)

    # Otherwise search in standard Windows system directories
    system_directories = []

    # Get Windows directory from environment variable
    windir = os.environ.get('WINDIR', 'C:\\Windows')
    system_directories.append(windir)
    system_directories.append(os.path.join(windir, 'System32'))

    # Add SysWOW64 on 64-bit Windows
    syswow64 = os.path.join(windir, 'SysWOW64')
    if os.path.exists(syswow64):
        system_directories.append(syswow64)

    # Add Program Files directories
    program_files = os.environ.get('ProgramFiles', 'C:\\Program Files')
    system_directories.append(program_files)

    program_files_x86 = os.environ.get('ProgramFiles(x86)', 'C:\\Program Files (x86)')
    if os.path.exists(program_files_x86):
        system_directories.append(program_files_x86)

    # Search each directory
    for directory in system_directories:
        if os.path.exists(directory):
            system_files.extend(
                find_by_windows_extension(['.exe', '.dll', '.sys'], directory)
            )

    return system_files


def search_menu_handler(current_path: str) -> bool:
    """
    Interactive search menu handler for Windows file system.

    Args:
        current_path (str): Current directory path.

    Returns:
        bool: True if user wants to continue searching, False to exit.
    """
    while True:
        print("\n" + "=" * 60)
        print("  WINDOWS FILE SEARCH MENU")
        print("=" * 60)
        print(f"  Current directory: {current_path}")
        print("-" * 60)
        print("  1. Search files by name/wildcard pattern")
        print("  2. Search files by extension")
        print("  3. Search large files")
        print("  4. Search Windows system files")
        print("  5. Show directory statistics")
        print("  0. Exit search menu")
        print("-" * 60)

        try:
            choice = input("\nSelect action (0-5): ").strip()

            match choice:
                case "1":
                    print("\n" + "-" * 60)
                    print("  SEARCH BY PATTERN")
                    print("-" * 60)
                    print("  Wildcards: * - any characters, ? - single character")
                    print("  Examples: *.txt, document?.docx, report_*.pdf")
                    print("-" * 60)

                    pattern = input("  Enter search pattern: ").strip()
                    if not pattern:
                        print("  ✗ Pattern cannot be empty!")
                        continue

                    case_sensitive = input("  Case sensitive? (y/N): ").strip().lower() == 'y'

                    print(f"\n  Searching for '{pattern}' in {current_path}...")
                    results = find_files_windows(pattern, current_path, case_sensitive)

                    format_windows_search_results(results, 'pattern', pattern=pattern)

                case "2":
                    print("\n" + "-" * 60)
                    print("  SEARCH BY EXTENSION")
                    print("-" * 60)
                    print("  Enter extensions separated by commas")
                    print("  Examples: .txt, exe, .pdf, dll")
                    print("-" * 60)

                    ext_input = input("  Extensions: ").strip()
                    if not ext_input:
                        print("  ✗ Extensions cannot be empty!")
                        continue

                    extensions = [e.strip() for e in ext_input.split(',') if e.strip()]
                    print(f"\n  Searching for {extensions} in {current_path}...")
                    results = find_by_windows_extension(extensions, current_path)

                    format_windows_search_results(results, 'extension', extensions=extensions)

                case "3":
                    print("\n" + "-" * 60)
                    print("  SEARCH LARGE FILES")
                    print("-" * 60)

                    min_size_input = input("  Minimum size in MB (default: 10): ").strip()
                    min_size_mb = float(min_size_input) if min_size_input else 10.0

                    print(f"\n  Searching for files > {min_size_mb} MB in {current_path}...")
                    results = find_large_files_windows(min_size_mb, current_path)

                    format_windows_search_results(results, 'large', min_size_mb=min_size_mb)

                case "4":
                    print("\n" + "-" * 60)
                    print("  SEARCH WINDOWS SYSTEM FILES")
                    print("-" * 60)
                    print("  ⚠  WARNING: System files are critical for Windows operation!")
                    print("  ⚠  DO NOT modify or delete these files unless you're absolutely sure.")
                    print("-" * 60)

                    search_choice = input(
                        "  Search in [C]urrent directory or [A]ll system locations? (C/A): ").strip().upper()

                    if search_choice == 'C':
                        print(f"\n  Searching system files in {current_path}...")
                        results = find_windows_system_files(current_path)
                    else:
                        print("\n  Searching all Windows system locations...")
                        results = find_windows_system_files()

                    format_windows_search_results(results, 'system')

                case "5":
                    print("\n" + "-" * 60)
                    print("  DIRECTORY STATISTICS")
                    print("-" * 60)
                    analysis.show_windows_directory_stats(current_path)

                case "0":
                    confirm = input("\n  Are you sure you want to exit search menu? (y/N): ").strip().lower()
                    if confirm == 'y':
                        print("  Exiting search menu. Goodbye!")
                        return False
                    continue

                case _:
                    print("  ✗ Invalid choice. Please select 0-5.")

            # Ask if user wants to continue after each operation
            if choice != "0":
                print("\n" + "-" * 60)
                continue_choice = input("  Press Enter to continue or '0' to exit menu: ").strip()
                if continue_choice == '0':
                    print("  Exiting search menu. Goodbye!")
                    return False

        except ValueError as e:
            print(f"  ✗ Invalid input: {e}")
        except KeyboardInterrupt:
            print("\n  Operation cancelled by user.")
            return False
        except Exception as e:
            print(f"  ✗ Error: {e}")


def format_windows_search_results(results: List, search_type: str, **kwargs) -> None:
    """
    Format and display search results based on search type.

    Args:
        results (List): Search results list (paths or file info dictionaries).
        search_type (str): Type of search ('pattern', 'extension', 'large', 'system').
        **kwargs: Additional parameters for display formatting.
    """
    if not results:
        print("\n  📁 No files found matching your criteria.")
        return

    print("\n" + "=" * 70)
    print(f"  SEARCH RESULTS ({len(results):,} files)")
    print("=" * 70)

    if search_type == 'pattern':
        pattern = kwargs.get('pattern', '')
        print(f"  Pattern: '{pattern}'")

        # Display first 20 files
        for i, file_path in enumerate(results[:20], 1):
            # Shorten path for display
            display_path = file_path
            if len(display_path) > 60:
                display_path = '...' + display_path[-57:]
            print(f"  {i:2d}. {display_path}")

        if len(results) > 20:
            print(f"  ... and {len(results) - 20} more files")

    elif search_type == 'extension':
        extensions = kwargs.get('extensions', [])
        print(f"  Extensions: {', '.join(extensions)}")

        # Group by extension
        by_extension = {}
        for file_path in results:
            _, ext = os.path.splitext(file_path)
            by_extension[ext] = by_extension.get(ext, 0) + 1

        print("\n  Files by extension:")
        for ext, count in sorted(by_extension.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"    {ext if ext else '(no ext)'}: {count}")

        # Display first 15 files
        print("\n  Sample files:")
        for i, file_path in enumerate(results[:15], 1):
            display_path = file_path
            if len(display_path) > 50:
                display_path = '...' + display_path[-47:]
            print(f"  {i:2d}. {display_path}")

    elif search_type == 'large':
        min_size_mb = kwargs.get('min_size_mb', 10)
        print(f"  Minimum size: {min_size_mb} MB")
        print(f"\n  {'#':<3} {'Size':>10} {'Extension':<12} {'Name':<40}")
        print(f"  {'-' * 3} {'-' * 10} {'-' * 12} {'-' * 40}")

        for i, file_info in enumerate(results[:15], 1):
            name_display = file_info['name']
            if len(name_display) > 37:
                name_display = name_display[:34] + '...'

            print(f"  {i:<3} {file_info['size_mb']:>8.2f} MB  {file_info['type']:<12} {name_display}")

        if len(results) > 15:
            print(f"\n  ... and {len(results) - 15} more large files")

    elif search_type == 'system':
        print("  ⚠  SYSTEM FILES - Handle with caution!")

        # Group by directory
        by_directory = {}
        for file_path in results:
            directory = os.path.dirname(file_path)
            by_directory[directory] = by_directory.get(directory, 0) + 1

        print("\n  Files by system directory:")
        for directory, count in sorted(by_directory.items(), key=lambda x: x[1], reverse=True):
            short_dir = directory
            if len(short_dir) > 40:
                short_dir = '...' + short_dir[-37:]
            print(f"    {short_dir}: {count} files")

        # Display sample
        if results:
            print("\n  Sample system files:")
            for i, file_path in enumerate(results[:10], 1):
                file_name = os.path.basename(file_path)
                directory = os.path.dirname(file_path)
                short_dir = directory
                if len(short_dir) > 30:
                    short_dir = '...' + short_dir[-27:]
                print(f"  {i:2d}. {file_name:<30} [{short_dir}]")

    # Additional statistics if available
    if utils.is_windows_os() and results and search_type not in ['large', 'system']:
        try:
            # Get attributes for first few files as sample
            sample_files = results[:5]
            hidden_count = 0
            readonly_count = 0

            for file_path in sample_files:
                if utils.is_hidden_windows_file(file_path):
                    hidden_count += 1

            if hidden_count > 0:
                print(f"\n  ⚠  {hidden_count} hidden file(s) in results")
        except Exception:
            pass

    print("=" * 70)
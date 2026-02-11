"""
Windows File System Explorer - Main Entry Point.
A comprehensive tool for navigating, analyzing, and searching Windows file systems.
"""

import os
import sys
import platform
from typing import NoReturn

import utils
import navigation
import analysis
import search


def check_windows_environment() -> bool:
    """
    Verify that the program is running on Windows operating system.

    Returns:
        bool: True if Windows, False otherwise.
        
    Exits:
        If not Windows, prints error and returns False for main to handle.
    """
    if utils.is_windows_os():
        return True
    else:
        print("=" * 60)
        print("  ERROR: Incompatible Operating System")
        print("=" * 60)
        print("  This program is designed specifically for Windows.")
        print(f"  Detected OS: {platform.system()} {platform.release()}")
        print("  Please run this program on a Windows system.")
        print("=" * 60)
        return False


def display_windows_banner() -> None:
    """Display Windows system information banner with drive details."""
    print("\n" + "=" * 70)
    print("  🪟 WINDOWS FILE SYSTEM EXPLORER")
    print("=" * 70)
    
    try:
        # Get system information
        current_drive = navigation.get_current_drive()
        available_drives = navigation.list_available_drives()
        
        # Format drives list
        drives_str = ', '.join(available_drives) if available_drives else 'None detected'
        
        # Get Windows version info
        windows_version = platform.platform()
        windows_release = platform.release()
        windows_version_num = platform.version()
        
        print(f"\n  📁 Current Drive:     {current_drive}")
        print(f"  💾 Available Drives:  {drives_str}")
        print(f"\n  💻 System Information:")
        print(f"     • Platform:  {windows_version}")
        print(f"     • Release:   Windows {windows_release}")
        print(f"     • Version:   {windows_version_num[:20]}...")
        
        # Get processor info
        processor = platform.processor()
        if processor:
            print(f"     • Processor: {processor}")
            
    except Exception as e:
        print(f"\n  ⚠  Warning: Could not retrieve some system information: {e}")
    
    print("\n" + "=" * 70)
    print("  Type 'help' for commands, 'exit' to quit")
    print("=" * 70)


def display_main_menu(current_path: str) -> None:
    """
    Display the main navigation menu with current path and available drives.
    
    Args:
        current_path (str): Current working directory.
    """
    print("\n" + "-" * 70)
    print(f"  📂 CURRENT DIRECTORY: {current_path}")
    print("-" * 70)
    
    try:
        available_drives = navigation.list_available_drives()
        if available_drives:
            drives_str = ', '.join(available_drives[:5])
            if len(available_drives) > 5:
                drives_str += f" and {len(available_drives) - 5} more"
            print(f"  💾 Available Drives: {drives_str}")
    except Exception:
        pass  # Silently fail if drives cannot be listed
    
    print("\n  📋 MAIN MENU:")
    print("  ┌─────────┬────────────────────────────────────────┐")
    print("  │ Command │ Description                            │")
    print("  ├─────────┼────────────────────────────────────────┤")
    print("  │    1    │ Navigation (move up/down, change drive)│")
    print("  │    2    │ Analysis (file stats, sizes, types)    │")
    print("  │    3    │ Search (pattern, extension, large)     │")
    print("  │    4    │ Show this menu                         │")
    print("  │    5    │ Show current path                      │")
    print("  │    0    │ Exit program                           │")
    print("  └─────────┴────────────────────────────────────────┘")


def handle_windows_navigation(current_path: str) -> str:
    """
    Handle Windows filesystem navigation commands.
    
    Args:
        current_path (str): Current directory path.
        
    Returns:
        str: Updated path after navigation.
    """
    print("\n" + "=" * 60)
    print("  🧭 NAVIGATION MENU")
    print("=" * 60)
    print(f"  Current: {current_path}")
    print("-" * 60)
    print("  1. Move to parent directory")
    print("  2. Move to subdirectory")
    print("  3. Change drive")
    print("  4. Return to main menu")
    print("-" * 60)
    
    try:
        choice = input("  Select option (1-4): ").strip()
        
        match choice:
            case "1":
                new_path = navigation.move_up(current_path)
                if new_path and new_path != current_path:
                    print(f"  ✅ Moved up to: {new_path}")
                    return new_path
                else:
                    print("  ⚠  Already at root directory or cannot move up")
                    return current_path
                    
            case "2":
                # List subdirectories
                success, items = navigation.list_directory(current_path)
                if not success or not items:
                    print("  ✗ Cannot list directory contents")
                    return current_path
                
                # Filter directories only
                directories = [item for item in items if item['type'] == 'dir']
                
                if not directories:
                    print("  ⚠  No subdirectories found")
                    return current_path
                
                print("\n  Available subdirectories:")
                for i, directory in enumerate(directories[:10], 1):
                    hidden = " (hidden)" if directory.get('hidden', False) else ""
                    print(f"  {i:2d}. {directory['name']}{hidden}")
                
                if len(directories) > 10:
                    print(f"  ... and {len(directories) - 10} more")
                
                dir_choice = input("\n  Enter directory name or number: ").strip()
                
                # Check if input is a number
                try:
                    idx = int(dir_choice) - 1
                    if 0 <= idx < len(directories):
                        target_dir = directories[idx]['name']
                    else:
                        print("  ✗ Invalid selection")
                        return current_path
                except ValueError:
                    # Input is a directory name
                    target_dir = dir_choice
                
                success, new_path = navigation.move_down(current_path, target_dir)
                if success:
                    print(f"  ✅ Moved to: {new_path}")
                    return new_path
                else:
                    print(f"  ✗ Cannot move to '{target_dir}': directory not found or inaccessible")
                    return current_path
                    
            case "3":
                available_drives = navigation.list_available_drives()
                if not available_drives:
                    print("  ✗ No available drives detected")
                    return current_path
                
                print("\n  Available drives:")
                for i, drive in enumerate(available_drives, 1):
                    print(f"  {i:2d}. {drive}")
                
                drive_choice = input("\n  Enter drive letter (e.g., C) or number: ").strip().upper()
                
                # Check if input is a number
                try:
                    idx = int(drive_choice) - 1
                    if 0 <= idx < len(available_drives):
                        new_drive = available_drives[idx]
                    else:
                        print("  ✗ Invalid selection")
                        return current_path
                except ValueError:
                    # Input is a drive letter
                    new_drive = drive_choice if drive_choice.endswith(':') else drive_choice + ':'
                    if new_drive not in available_drives:
                        print(f"  ✗ Drive {new_drive} is not available")
                        return current_path
                
                # Validate the drive path
                is_valid, error_msg = utils.validate_windows_path(new_drive)
                if is_valid:
                    print(f"  ✅ Changed drive to: {new_drive}")
                    return new_drive
                else:
                    print(f"  ✗ Invalid drive: {error_msg}")
                    return current_path
                    
            case "4":
                print("  ↩  Returning to main menu")
                return current_path
                
            case _:
                print("  ✗ Invalid option. Please select 1-4.")
                return current_path
                
    except KeyboardInterrupt:
        print("\n  ⚠  Navigation cancelled")
        return current_path
    except Exception as e:
        print(f"  ✗ Navigation error: {e}")
        return current_path


def handle_windows_analysis(current_path: str) -> None:
    """
    Handle Windows filesystem analysis commands.
    
    Args:
        current_path (str): Directory path to analyze.
    """
    print("\n" + "=" * 60)
    print("  📊 ANALYSIS MENU")
    print("=" * 60)
    
    try:
        analysis.show_windows_directory_stats(current_path)
    except KeyboardInterrupt:
        print("\n  ⚠  Analysis cancelled")
    except Exception as e:
        print(f"  ✗ Analysis error: {e}")


def handle_windows_search(current_path: str) -> None:
    """
    Handle Windows filesystem search commands.
    
    Args:
        current_path (str): Directory path to search in.
    """
    print("\n" + "=" * 60)
    print("  🔍 SEARCH MENU")
    print("=" * 60)
    
    try:
        # search_menu_handler now returns bool (True to continue, False to exit)
        # We want to stay in search menu until user chooses to exit
        search.search_menu_handler(current_path)
    except KeyboardInterrupt:
        print("\n  ⚠  Search cancelled")
    except Exception as e:
        print(f"  ✗ Search error: {e}")


def run_windows_command(command: str, current_path: str) -> tuple[str, bool]:
    """
    Main command router using match case pattern matching.
    
    Args:
        command (str): User command input.
        current_path (str): Current directory path.
        
    Returns:
        tuple[str, bool]: (Updated current path, should_continue)
        - Updated path after command execution
        - Boolean indicating whether program should continue (False = exit)
    """
    match command.lower().strip():
        case "1" | "nav" | "navigation":
            return handle_windows_navigation(current_path), True
            
        case "2" | "analysis" | "analyze" | "stats":
            handle_windows_analysis(current_path)
            return current_path, True
            
        case "3" | "search" | "find":
            handle_windows_search(current_path)
            return current_path, True
            
        case "4" | "menu" | "help":
            display_main_menu(current_path)
            return current_path, True
            
        case "5" | "path" | "pwd":
            print(f"\n  📂 Current path: {current_path}")
            return current_path, True
            
        case "0" | "exit" | "quit":
            print("\n  👋 Thank you for using Windows File System Explorer!")
            print("  Goodbye!")
            return current_path, False
            
        case "drives":
            try:
                drives = navigation.list_available_drives()
                print(f"\n  💾 Available drives: {', '.join(drives)}")
            except Exception as e:
                print(f"  ✗ Error listing drives: {e}")
            return current_path, True
            
        case "banner":
            display_windows_banner()
            return current_path, True
            
        case "":
            return current_path, True
            
        case _:
            print(f"\n  ✗ Unknown command: '{command}'")
            print("  Type 'menu' or '4' to see available commands")
            return current_path, True


def main_loop(current_path: str) -> NoReturn:
    """
    Recursive main program loop without while True.
    
    Args:
        current_path (str): Starting directory path.
        
    Returns:
        NoReturn: This function either calls itself recursively or exits.
    """
    # Display command prompt and get user input
    print()
    try:
        command = input(f"  [{current_path}]> ").strip()
        
        # Process command and get updated path and continue flag
        new_path, should_continue = run_windows_command(command, current_path)
        
        # Recursive call if should continue
        if should_continue:
            main_loop(new_path)
        else:
            # Exit point - natural function return
            sys.exit(0)
            
    except KeyboardInterrupt:
        print("\n\n  ⚠  Interrupted by user")
        confirm = input("  Press Ctrl+C again to exit, or Enter to continue: ").strip()
        if not confirm:  # Enter pressed
            main_loop(current_path)  # Continue recursively
        else:
            print("\n  👋 Goodbye!")
            sys.exit(0)
            
    except EOFError:
        print("\n  👋 Goodbye!")
        sys.exit(0)
        
    except Exception as e:
        print(f"\n  ✗ Unexpected error: {e}")
        print("  Please report this issue.")
        # Continue recursively despite error
        main_loop(current_path)


def main() -> NoReturn:
    """
    Main program entry point.
    
    Performs:
    1. Windows environment verification
    2. Display welcome banner
    3. Initialize starting path
    4. Display initial menu
    5. Start recursive main loop
    """
    # Step 1: Check Windows environment
    if not check_windows_environment():
        sys.exit(1)
    
    # Step 2: Display welcome banner
    display_windows_banner()
    
    # Step 3: Initialize starting path
    try:
        current_path = os.getcwd()
    except Exception:
        # Fallback to root of current drive
        current_drive = navigation.get_current_drive()
        current_path = current_drive if current_drive else "C:\\"
    
    # Step 4: Display initial menu
    display_main_menu(current_path)
    
    # Step 5: Start recursive main loop (no while True, no flags)
    main_loop(current_path)


if __name__ == "__main__":
    main()
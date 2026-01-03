"""
Nova Actions - OS Automation Functions
High-level automation actions for desktop control.
"""

import os
import time
import shutil
import subprocess
import pyautogui
import psutil
import datetime
import pygetwindow as gw

# Import path utilities from package
from app import get_runtime_audio_file


# =============================================================================
# WINDOWS SHORTCUT INTELLIGENCE SYSTEM
# =============================================================================

# SHORTCUT KNOWLEDGE BASE - Dictionary of all Windows shortcuts
WINDOWS_SHORTCUTS = {
    # SYSTEM & WINDOW CONTROL
    "lock_pc": {"keys": ["win", "l"], "description": "Lock the computer"},
    "task_manager": {"keys": ["ctrl", "shift", "esc"], "description": "Open Task Manager"},
    "close_app": {"keys": ["alt", "F4"], "description": "Close current application"},
    "switch_window": {"keys": ["alt", "tab"], "description": "Switch to next window"},
    "show_desktop": {"keys": ["win", "d"], "description": "Show desktop"},
    "minimize_all": {"keys": ["win", "m"], "description": "Minimize all windows"},
    "restore_windows": {"keys": ["win", "shift", "m"], "description": "Restore minimized windows"},
    "snap_left": {"keys": ["win", "left"], "description": "Snap window to left"},
    "snap_right": {"keys": ["win", "right"], "description": "Snap window to right"},
    "maximize_window": {"keys": ["win", "up"], "description": "Maximize window"},
    "minimize_window": {"keys": ["win", "down"], "description": "Minimize current window"},
    
    # FILE & EXPLORER
    "file_explorer": {"keys": ["win", "e"], "description": "Open File Explorer"},
    "new_folder": {"keys": ["ctrl", "shift", "n"], "description": "Create new folder"},
    "rename": {"keys": ["F2"], "description": "Rename selected item"},
    "search": {"keys": ["ctrl", "f"], "description": "Open search/find"},
    "select_all": {"keys": ["ctrl", "a"], "description": "Select all"},
    "delete": {"keys": ["delete"], "description": "Delete selected item"},
    "permanent_delete": {"keys": ["shift", "delete"], "description": "Permanently delete"},
    
    # SCREEN & DISPLAY
    "screenshot_full": {"keys": ["win", "prtsc"], "description": "Full screenshot"},
    "screenshot_snip": {"keys": ["win", "shift", "s"], "description": "Screenshot snip tool"},
    "project_display": {"keys": ["win", "p"], "description": "Project display settings"},
    "open_settings": {"keys": ["win", "i"], "description": "Open Windows Settings"},
    
    # TEXT & EDITING
    "copy": {"keys": ["ctrl", "c"], "description": "Copy"},
    "paste": {"keys": ["ctrl", "v"], "description": "Paste"},
    "cut": {"keys": ["ctrl", "x"], "description": "Cut"},
    "undo": {"keys": ["ctrl", "z"], "description": "Undo"},
    "redo": {"keys": ["ctrl", "y"], "description": "Redo"},
    "save": {"keys": ["ctrl", "s"], "description": "Save"},
    "save_as": {"keys": ["ctrl", "shift", "s"], "description": "Save as"},
    "print": {"keys": ["ctrl", "p"], "description": "Print"},
    "find": {"keys": ["ctrl", "f"], "description": "Find"},
    
    # BROWSER COMMON ACTIONS
    "new_tab": {"keys": ["ctrl", "t"], "description": "New browser tab"},
    "close_tab": {"keys": ["ctrl", "w"], "description": "Close current tab"},
    "reopen_tab": {"keys": ["ctrl", "shift", "t"], "description": "Reopen closed tab"},
    "switch_tab": {"keys": ["ctrl", "tab"], "description": "Switch to next tab"},
    "refresh": {"keys": ["ctrl", "r"], "description": "Refresh page"},
    "address_bar": {"keys": ["ctrl", "l"], "description": "Focus address bar"},
    "new_browser_window": {"keys": ["ctrl", "n"], "description": "New browser window"},
    "incognito": {"keys": ["ctrl", "shift", "n"], "description": "Open incognito/private window"},
    
    # ADDITIONAL USEFUL SHORTCUTS
    "run_dialog": {"keys": ["win", "r"], "description": "Open Run dialog"},
    "action_center": {"keys": ["win", "a"], "description": "Open Action Center"},
    "clipboard_history": {"keys": ["win", "v"], "description": "Open clipboard history"},
    "emoji_picker": {"keys": ["win", "."], "description": "Open emoji picker"},
    "virtual_desktop_new": {"keys": ["win", "ctrl", "d"], "description": "Create new virtual desktop"},
    "virtual_desktop_close": {"keys": ["win", "ctrl", "F4"], "description": "Close virtual desktop"},
    "virtual_desktop_switch": {"keys": ["win", "ctrl", "left"], "description": "Switch virtual desktop"},
    "zoom_in": {"keys": ["ctrl", "plus"], "description": "Zoom in"},
    "zoom_out": {"keys": ["ctrl", "minus"], "description": "Zoom out"},
    "zoom_reset": {"keys": ["ctrl", "0"], "description": "Reset zoom"},
}

# INTENT MATCHING RULES - Maps natural language phrases to shortcut keys
INTENT_PATTERNS = {
    # SYSTEM CONTROL
    "lock_pc": [
        "lock", "lock pc", "lock my pc", "lock the computer", "lock computer",
        "lock my computer", "lock screen", "lock my screen", "lock system",
        "lock my system", "lock this", "secure the computer", "secure pc"
    ],
    "task_manager": [
        "task manager", "open task manager", "show task manager", "processes",
        "show processes", "system processes", "kill process", "end task",
        "performance monitor", "open processes"
    ],
    "close_app": [
        "close", "close this", "close app", "close application", "close this app",
        "close window", "close this window", "exit", "exit app", "exit this",
        "kill this", "kill window", "kill app", "shut this", "terminate",
        "close the app", "close the window", "quit", "quit app", "quit this"
    ],
    "switch_window": [
        "switch window", "switch windows", "next window", "change window",
        "go to next window", "alt tab", "switch app", "switch application",
        "change app", "next app", "go to next app", "toggle window",
        "switch to another window", "cycle windows", "window switch"
    ],
    "show_desktop": [
        "show desktop", "go to desktop", "desktop", "see desktop",
        "minimize everything", "hide all", "clear screen", "go desktop"
    ],
    "minimize_all": [
        "minimize all", "minimize everything", "minimize all windows",
        "hide everything", "hide all windows", "clear all windows",
        "minimize windows", "put away windows"
    ],
    "restore_windows": [
        "restore windows", "restore all", "restore all windows",
        "bring back windows", "unminimize", "show all windows",
        "bring windows back", "restore minimized"
    ],
    "snap_left": [
        "snap left", "window left", "snap window left", "move left",
        "move window left", "tile left", "dock left", "put window left"
    ],
    "snap_right": [
        "snap right", "window right", "snap window right", "move right",
        "move window right", "tile right", "dock right", "put window right"
    ],
    "maximize_window": [
        "maximize", "maximize window", "maximize this", "full screen",
        "make window bigger", "expand window", "make bigger", "fullscreen"
    ],
    "minimize_window": [
        "minimize", "minimize window", "minimize this", "make smaller",
        "shrink window", "put away", "hide window", "hide this window"
    ],
    
    # FILE & EXPLORER
    "file_explorer": [
        "file explorer", "open explorer", "explorer", "open files",
        "show files", "my files", "open my files", "show my files",
        "open file explorer", "files", "folder", "open folder",
        "windows explorer", "browse files", "file browser"
    ],
    "new_folder": [
        "new folder", "create folder", "make folder", "add folder",
        "create new folder", "make new folder"
    ],
    "rename": [
        "rename", "rename this", "rename file", "rename folder",
        "change name", "edit name"
    ],
    "select_all": [
        "select all", "select everything", "highlight all", "choose all"
    ],
    "delete": [
        "delete", "delete this", "remove", "remove this", "trash"
    ],
    "permanent_delete": [
        "permanent delete", "delete permanently", "delete forever",
        "remove permanently", "shift delete"
    ],
    
    # SCREEN & DISPLAY
    "screenshot_full": [
        "screenshot", "take screenshot", "capture screen", "screen capture",
        "print screen", "full screenshot", "capture this screen"
    ],
    "screenshot_snip": [
        "snip", "snip tool", "snipping tool", "snip this", "partial screenshot",
        "capture area", "capture region", "screenshot region", "screen snip",
        "snip screenshot", "clip this", "clip screen"
    ],
    "project_display": [
        "project", "project display", "display settings", "projector",
        "extend display", "duplicate display", "second screen", "external display"
    ],
    "open_settings": [
        "settings", "open settings", "windows settings", "system settings",
        "control panel", "preferences", "options", "pc settings"
    ],
    
    # TEXT & EDITING
    "copy": [
        "copy", "copy this", "copy text", "copy that"
    ],
    "paste": [
        "paste", "paste this", "paste text", "paste that"
    ],
    "cut": [
        "cut", "cut this", "cut text", "cut that"
    ],
    "undo": [
        "undo", "undo that", "undo this", "go back", "reverse", "revert"
    ],
    "redo": [
        "redo", "redo that", "redo this", "go forward"
    ],
    "save": [
        "save", "save this", "save file", "save document", "save it"
    ],
    "save_as": [
        "save as", "save as new", "save copy", "save to new file"
    ],
    "print": [
        "print", "print this", "print document", "print file", "printer"
    ],
    "find": [
        "find", "find text", "search text", "search in page", "find in page",
        "look for", "search for"
    ],
    
    # BROWSER ACTIONS
    "new_tab": [
        "new tab", "open new tab", "add tab", "create tab", "open tab"
    ],
    "close_tab": [
        "close tab", "close this tab", "close current tab", "remove tab"
    ],
    "reopen_tab": [
        "reopen tab", "restore tab", "bring back tab", "undo close tab",
        "open closed tab", "reopen closed tab"
    ],
    "switch_tab": [
        "switch tab", "next tab", "change tab", "go to next tab", "cycle tab"
    ],
    "refresh": [
        "refresh", "reload", "refresh page", "reload page", "update page"
    ],
    "address_bar": [
        "address bar", "url bar", "go to address bar", "focus address bar",
        "type url", "enter url"
    ],
    "new_browser_window": [
        "new window", "open new window", "new browser window"
    ],
    "incognito": [
        "incognito", "private window", "private browsing", "incognito mode",
        "open incognito", "open private", "private mode"
    ],
    
    # ADDITIONAL SHORTCUTS
    "run_dialog": [
        "run", "run dialog", "open run", "run command", "run box"
    ],
    "action_center": [
        "action center", "notifications", "notification center", "alerts"
    ],
    "clipboard_history": [
        "clipboard", "clipboard history", "paste history", "copy history"
    ],
    "emoji_picker": [
        "emoji", "emoji picker", "emojis", "insert emoji", "open emoji"
    ],
    "virtual_desktop_new": [
        "new desktop", "create desktop", "new virtual desktop", "add desktop"
    ],
    "virtual_desktop_close": [
        "close desktop", "close virtual desktop", "remove desktop"
    ],
    "virtual_desktop_switch": [
        "switch desktop", "change desktop", "next desktop", "other desktop"
    ],
    "zoom_in": [
        "zoom in", "make bigger", "enlarge", "increase size"
    ],
    "zoom_out": [
        "zoom out", "make smaller", "reduce", "decrease size"
    ],
    "zoom_reset": [
        "reset zoom", "normal zoom", "100%", "actual size"
    ],
    "search": [
        "search", "find", "control f", "search bar"
    ],
}


def normalize_intent(text):
    """
    Normalize the input text for intent matching.
    Removes punctuation, converts to lowercase, strips extra spaces.
    
    Args:
        text: Raw user speech text
        
    Returns:
        Cleaned, normalized text
    """
    import re
    # Convert to lowercase
    text = text.lower().strip()
    # Remove punctuation except hyphens and spaces
    text = re.sub(r'[^\w\s-]', '', text)
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    return text


def match_intent(text):
    """
    Match user text to a shortcut intent using keyword matching.
    Uses priority scoring: exact match > contains > partial match.
    
    Args:
        text: Normalized user speech text
        
    Returns:
        Tuple of (shortcut_key, confidence) or (None, 0) if no match
    """
    text = normalize_intent(text)
    
    best_match = None
    best_score = 0
    
    for shortcut_key, patterns in INTENT_PATTERNS.items():
        for pattern in patterns:
            pattern_lower = pattern.lower()
            
            # EXACT MATCH - Highest priority
            if text == pattern_lower:
                return (shortcut_key, 1.0)
            
            # CONTAINS - High priority (text contains the pattern)
            if pattern_lower in text:
                # Score based on how much of the text the pattern covers
                score = len(pattern_lower) / len(text) * 0.9
                if score > best_score:
                    best_score = score
                    best_match = shortcut_key
            
            # PARTIAL MATCH - Medium priority (pattern words in text)
            else:
                pattern_words = set(pattern_lower.split())
                text_words = set(text.split())
                common_words = pattern_words & text_words
                
                if common_words and len(common_words) >= len(pattern_words) * 0.5:
                    score = len(common_words) / len(pattern_words) * 0.7
                    if score > best_score:
                        best_score = score
                        best_match = shortcut_key
    
    # Only return if confidence is above threshold
    if best_score >= 0.4:
        return (best_match, best_score)
    
    return (None, 0)


def execute_windows_shortcut(intent_text, status_callback=None):
    """
    Main entry point for Windows Shortcut Intelligence.
    
    This function:
    1. Receives normalized intent text from speech
    2. Matches it to the best shortcut using intent matching
    3. Executes the shortcut using pyautogui.hotkey()
    4. Returns success/failure status with UI feedback
    
    Args:
        intent_text: The user's speech text (e.g., "open task manager")
        status_callback: Optional callback function for UI status updates
        
    Returns:
        Dictionary with:
        - success: bool
        - action: The action executed (or None)
        - description: Human-readable description
        - confidence: Match confidence (0.0 - 1.0)
    """
    print(f"🎯 SHORTCUT INTEL: Processing '{intent_text}'...")
    
    # Step 1: Normalize and match intent
    shortcut_key, confidence = match_intent(intent_text)
    
    if shortcut_key is None or confidence < 0.4:
        print(f"   ❌ No confident match found (confidence: {confidence:.2f})")
        result = {
            "success": False,
            "action": None,
            "description": "Command not recognized. Could not map to a Windows shortcut.",
            "confidence": confidence
        }
        if status_callback:
            status_callback("Command not recognized")
        return result
    
    # Step 2: Get the shortcut configuration
    shortcut_config = WINDOWS_SHORTCUTS.get(shortcut_key)
    if not shortcut_config:
        print(f"   ❌ Shortcut key '{shortcut_key}' not found in knowledge base")
        return {
            "success": False,
            "action": shortcut_key,
            "description": f"Shortcut '{shortcut_key}' not configured.",
            "confidence": confidence
        }
    
    keys = shortcut_config["keys"]
    description = shortcut_config["description"]
    
    print(f"   ✅ Matched: {shortcut_key} (confidence: {confidence:.2f})")
    print(f"   📋 Keys: {'+'.join(keys)}")
    print(f"   📝 Action: {description}")
    
    # Step 3: Safety delay before execution
    time.sleep(0.2)
    
    # Step 4: Execute the shortcut
    try:
        if len(keys) == 1:
            pyautogui.press(keys[0])
        else:
            pyautogui.hotkey(*keys)
        
        # Small delay after execution
        time.sleep(0.3)
        
        print(f"   ✅ Executed: {description}")
        
        # Update UI status
        if status_callback:
            status_callback(f"Executed: {description}")
        
        return {
            "success": True,
            "action": shortcut_key,
            "description": f"Executed: {description}",
            "confidence": confidence
        }
        
    except Exception as e:
        print(f"   ❌ Execution failed: {e}")
        if status_callback:
            status_callback(f"Execution failed: {str(e)}")
        return {
            "success": False,
            "action": shortcut_key,
            "description": f"Command recognized but execution failed: {str(e)}",
            "confidence": confidence
        }


def get_available_shortcuts():
    """
    Returns a list of all available shortcuts with their descriptions.
    Useful for help/listing functionality.
    
    Returns:
        List of dictionaries with shortcut info
    """
    shortcuts = []
    for key, config in WINDOWS_SHORTCUTS.items():
        shortcuts.append({
            "key": key,
            "keys": config["keys"],
            "description": config["description"],
            "hotkey": "+".join(config["keys"])
        })
    return shortcuts


def get_shortcut_categories():
    """
    Returns shortcuts organized by category.
    
    Returns:
        Dictionary with categories as keys
    """
    categories = {
        "System Control": ["lock_pc", "task_manager", "close_app", "switch_window", 
                          "show_desktop", "minimize_all", "restore_windows",
                          "snap_left", "snap_right", "maximize_window", "minimize_window"],
        "File Explorer": ["file_explorer", "new_folder", "rename", "select_all",
                         "delete", "permanent_delete"],
        "Screen & Display": ["screenshot_full", "screenshot_snip", "project_display", 
                            "open_settings"],
        "Text Editing": ["copy", "paste", "cut", "undo", "redo", "save", "save_as",
                        "print", "find"],
        "Browser": ["new_tab", "close_tab", "reopen_tab", "switch_tab", "refresh",
                   "address_bar", "new_browser_window", "incognito"],
        "Productivity": ["run_dialog", "action_center", "clipboard_history", 
                        "emoji_picker", "virtual_desktop_new", "virtual_desktop_close",
                        "virtual_desktop_switch", "zoom_in", "zoom_out", "zoom_reset", "search"],
    }
    
    result = {}
    for category, keys in categories.items():
        result[category] = []
        for key in keys:
            if key in WINDOWS_SHORTCUTS:
                config = WINDOWS_SHORTCUTS[key]
                result[category].append({
                    "key": key,
                    "hotkey": "+".join(config["keys"]),
                    "description": config["description"]
                })
    
    return result


# --- VISIBILITY ENFORCER ---
def force_foreground(app_name):
    """
    Finds a window by name and aggressively brings it to the front.
    """
    # Loop for up to 5 seconds waiting for the window
    for _ in range(10):
        try:
            windows = gw.getWindowsWithTitle(app_name)
            if windows:
                win = windows[0]
                if win.isMinimized:
                    win.restore()
                win.activate()
                return True
        except:
            pass
        time.sleep(0.5)
    return False


# --- KNOWN SITES DICTIONARY ---
KNOWN_SITES = {
    "olx": "olx.com.pk",
    "youtube": "youtube.com",
    "facebook": "facebook.com",
    # "whatsapp" removed - use Desktop App via launch_app() instead
    "chatgpt": "chatgpt.com",
    "github": "github.com",
    "gmail": "mail.google.com",
    "google": "google.com",
    "twitter": "twitter.com",
    "x": "x.com",
    "reddit": "reddit.com",
    "linkedin": "linkedin.com",
    "instagram": "instagram.com",
    "amazon": "amazon.com",
    "netflix": "netflix.com",
    "spotify": "open.spotify.com",
    "stackoverflow": "stackoverflow.com",
    "stack overflow": "stackoverflow.com",
    "wikipedia": "wikipedia.org",
    "pinterest": "pinterest.com",
    "tiktok": "tiktok.com",
    "twitch": "twitch.tv",
    "discord": "discord.com",
}


# --- UNIVERSAL APP LAUNCHER ---
def launch_app(app_name, wait_time=2.0):
    """
    Robust Universal Launcher.
    Uses "Focus Anchor" (click center of screen) to guarantee OS focus.
    Smart Maximize: Only maximizes if window is not already maximized.
    """
    print(f"🚀 LAUNCH: Starting '{app_name}' via Start Menu...")
    
    # Step 1: Press Windows key
    pyautogui.press('win')
    time.sleep(0.3)
    
    # Step 2: Type app name
    pyautogui.write(app_name, interval=0.05)
    time.sleep(0.3)
    
    # Step 3: Press Enter to launch
    pyautogui.press('enter')
    
    # Step 4: CRITICAL WAIT - Let the window fully appear
    print(f"   -> Waiting for '{app_name}' window (2.0s)...")
    time.sleep(2.0)
    
    # Step 5: THE FOCUS ANCHOR - Click dead center of screen
    # This GUARANTEES the OS focuses the new window (not VS Code)
    w, h = pyautogui.size()
    center_x = int(w * 0.5)
    center_y = int(h * 0.5)
    print(f"   -> Focus Anchor: Clicking center ({center_x}, {center_y})...")
    pyautogui.click(center_x, center_y)
    time.sleep(0.3)
    
    # Step 6: SMART MAXIMIZE - Only if not already maximized
    print(f"   -> Checking window state...")
    try:
        windows = gw.getWindowsWithTitle(app_name)
        if windows:
            win = windows[0]
            if not win.isMaximized:
                print(f"   -> Window not maximized. Maximizing now...")
                try:
                    win.maximize()
                    time.sleep(0.5)
                except:
                    # Fallback if .maximize() fails
                    print(f"   -> .maximize() failed, using Win+Up fallback...")
                    pyautogui.hotkey('win', 'up')
                    time.sleep(0.5)
            else:
                print(f"   -> Window already maximized. Skipping.")
        else:
            # Window not found by name, use Win+Up as fallback
            print(f"   -> Window not found by name, using Win+Up fallback...")
            pyautogui.hotkey('win', 'up')
            time.sleep(0.5)
    except Exception as e:
        print(f"   -> Smart maximize failed: {e}, using Win+Up fallback...")
        pyautogui.hotkey('win', 'up')
        time.sleep(0.5)
    
    print(f"   ✅ '{app_name}' ready.")
    return True


# Legacy alias for backward compatibility
def launch_human_browser():
    """Launches Brave browser using universal launcher."""
    return launch_app("Brave", wait_time=2.0)


def browser_navigate(payload):
    """
    Navigates to URL or performs search using keyboard macros.
    Assumes browser is already open.
    """
    # Focus address bar
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.2)
    
    # Clear any existing text
    pyautogui.hotkey('ctrl', 'a')
    time.sleep(0.1)
    
    # Type the payload (URL or search query)
    pyautogui.write(payload, interval=0.02)
    time.sleep(0.1)
    
    # Press Enter to navigate/search
    pyautogui.press('enter')
    
    return f"Navigated to: {payload}"


# --- KNOWN DOWNLOAD URLs ---
DIRECT_URLS = {
    "vlc": "https://www.videolan.org/vlc/download-windows.html",
    "chrome": "https://www.google.com/chrome/",
    "steam": "https://store.steampowered.com/about/",
    "discord": "https://discord.com/download",
    "firefox": "https://www.mozilla.org/en-US/firefox/new/",
    "spotify": "https://www.spotify.com/download/windows/",
    "vscode": "https://code.visualstudio.com/download",
    "vs code": "https://code.visualstudio.com/download",
    "visual studio code": "https://code.visualstudio.com/download",
    "brave": "https://brave.com/download/",
    "zoom": "https://zoom.us/download",
    "obs": "https://obsproject.com/download",
    "git": "https://git-scm.com/download/win",
    "python": "https://www.python.org/downloads/",
    "node": "https://nodejs.org/en/download/",
    "nodejs": "https://nodejs.org/en/download/",
    "7zip": "https://www.7-zip.org/download.html",
    "winrar": "https://www.win-rar.com/download.html",
    "notepad++": "https://notepad-plus-plus.org/downloads/",
    "audacity": "https://www.audacityteam.org/download/",
    "gimp": "https://www.gimp.org/downloads/",
    "blender": "https://www.blender.org/download/",
}


def handle_web_download(app_name):
    """
    Human-like web downloading using standard Google search.
    Phase 1: Navigate to download page via open_smart_website
    Phase 2: Ctrl+F -> Find "Download" -> Esc -> Enter to click
    """
    print(f"📥 DOWNLOAD: Initiating download for '{app_name}'...")
    
    app_key = app_name.lower().strip()
    
    # PHASE 1: NAVIGATE TO DOWNLOAD PAGE
    if app_key in DIRECT_URLS:
        # Known app - go directly to download URL
        target_url = DIRECT_URLS[app_key]
        print(f"   -> Known app! Direct URL: {target_url}")
        
        launch_app("Brave")
        pyautogui.hotkey('ctrl', 'l')
        time.sleep(0.3)
        pyautogui.write(target_url, interval=0.01)
        pyautogui.press('enter')
    else:
        # Unknown app - use standard Google search (no Lucky links!)
        search_query = f"{app_name} download"
        print(f"   -> Unknown app. Searching: '{search_query}'")
        open_smart_website(search_query)
    
    # PHASE 2: WAIT FOR PAGE TO FULLY LOAD
    print("   -> Waiting for download page to load (4.5s)...")
    time.sleep(4.5)
    
    # PHASE 3: THE "FIND & CLICK" PROTOCOL
    print("   -> Find & Click Protocol...")
    
    # Open Find bar
    print("   -> Opening Find bar (Ctrl+F)...")
    pyautogui.hotkey('ctrl', 'f')
    time.sleep(0.3)
    
    # Type search term
    print("   -> Typing 'Download'...")
    pyautogui.write("Download", interval=0.03)
    time.sleep(0.2)
    
    # Press Enter to highlight first match
    print("   -> Highlighting match (Enter)...")
    pyautogui.press('enter')
    time.sleep(0.3)
    
    # CRITICAL FIX: Press Esc to close Find Bar
    # This returns focus to the highlighted page element
    print("   -> CRITICAL: Closing Find Bar (Esc)...")
    pyautogui.press('escape')
    time.sleep(0.5)
    
    # Now press Enter to click the highlighted/focused button
    print("   -> Clicking download button (Enter)...")
    pyautogui.press('enter')
    time.sleep(1.0)
    
    print("   ✅ Download sequence complete!")
    return f"Navigated to download page for {app_name} and attempted click."


def play_music_on_youtube(song_name):
    """
    One-Shot YouTube Method: Brave -> Ctrl+L -> URL -> Single Click -> DONE.
    NO Space, NO redundant clicks (these pause auto-play).
    """
    print(f"🎵 YOUTUBE: Attempting to play: '{song_name}'")
    
    # SAFETY: Abort if song name is too short (likely misheard)
    if len(song_name) < 2:
        print("   ❌ ABORT: Song name too short. Likely a hearing error.")
        return "Song name too short. Could you repeat that?"
    
    # STEP 1: LAUNCH BRAVE (Focus Anchor + Maximize)
    print("   -> Step 1: Launching Brave browser...")
    launch_app("Brave")
    
    # STEP 2: FOCUS ADDRESS BAR (Ctrl+L)
    print("   -> Step 2: Focusing address bar (Ctrl+L)...")
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.3)
    
    # STEP 3: CONSTRUCT AND TYPE URL
    print("   -> Step 3: Navigating to YouTube search...")
    query = song_name.replace(' ', '+')
    url = f"https://www.youtube.com/results?search_query={query}"
    
    print(f"   -> URL: {url}")
    pyautogui.write(url, interval=0.01)
    time.sleep(0.1)
    pyautogui.press('enter')
    
    # STEP 4: WAIT FOR YOUTUBE TO LOAD
    print("   -> Step 4: Waiting for YouTube results (3.5s)...")
    time.sleep(3.5)
    
    # STEP 5: THE CALIBRATED STRIKE - ONE CLICK ONLY
    w, h = pyautogui.size()
    print(f"   -> Screen size: {w}x{h}")
    
    # Click Zone: Thumbnail center (y=0.38 avoids preview overlay)
    click_x = int(w * 0.35)
    click_y = int(h * 0.38)
    print(f"   -> Calibrated Strike: ({click_x}, {click_y})")
    pyautogui.click(click_x, click_y)
    
    # CRITICAL: Function ends here. NO Space, NO second click.
    # YouTube auto-plays. Any interaction PAUSES it.
    
    print(f"   ✅ Playing '{song_name}' on YouTube.")
    return f"Playing '{song_name}' on YouTube."


# Legacy alias for backward compatibility
def play_music_on_spotify(song_name):
    """Redirects to YouTube player."""
    return play_music_on_youtube(song_name)


def open_smart_website(site_name):
    """
    Classic Website Method: Brave -> Ctrl+L -> URL/Search.
    Single-window strategy (no new tabs).
    Uses KNOWN_SITES for direct navigation.
    """
    print(f"🌐 SMART NAV: Opening '{site_name}'...")
    
    # STEP 1: LAUNCH BRAVE (Focus Anchor + Smart Maximize)
    launch_app("Brave")
    
    # STEP 2: FOCUS ADDRESS BAR (Ctrl+L)
    print("   -> Focusing address bar (Ctrl+L)...")
    pyautogui.hotkey('ctrl', 'l')
    time.sleep(0.3)
    
    # STEP 3: CHECK KNOWLEDGE BASE
    # Clean input: lowercase and remove spaces for flexible matching
    site_key = site_name.lower().replace(" ", "").strip()
    
    if site_key in KNOWN_SITES:
        # DIRECT KNOWLEDGE - Go straight to URL
        direct_url = KNOWN_SITES[site_key]
        print(f"   -> 🧠 KNOWN SITE: {direct_url}")
        
        pyautogui.write(direct_url, interval=0.02)
        time.sleep(0.1)
        pyautogui.press('enter')
        
        # Wait for page to load
        time.sleep(2.0)
        
        print(f"   ✅ Opened {site_name} directly.")
        return f"Opening {site_name} directly."
    
    else:
        # UNKNOWN SITE - Fall back to Google Search
        print(f"   -> 🔍 UNKNOWN SITE: Using Google search...")
        
        # Type site name (triggers Google search via address bar)
        pyautogui.write(site_name, interval=0.03)
        time.sleep(0.2)
        pyautogui.press('enter')
        
        # Wait for Google to load
        print("   -> Waiting for Google results (3.5s)...")
        time.sleep(3.5)
        
        # CALIBRATED SCATTER CLICK - Handles "Did you mean" layout shifts
        # Order: Low -> Right Panel -> Mid (maximizes chance of hitting real link)
        w, h = pyautogui.size()
        print(f"   -> Screen size: {w}x{h}")
        
        # Click 1: "Safe Low" - Below any "Did you mean" banners
        click1_x = int(w * 0.18)
        click1_y = int(h * 0.55)
        print(f"   -> Click 1 (Safe Low): ({click1_x}, {click1_y})")
        pyautogui.click(click1_x, click1_y)
        time.sleep(0.1)
        
        # Click 2: "Knowledge Panel" - Right side Visit button (if company card shown)
        click2_x = int(w * 0.85)
        click2_y = int(h * 0.35)
        print(f"   -> Click 2 (Knowledge Panel): ({click2_x}, {click2_y})")
        pyautogui.click(click2_x, click2_y)
        time.sleep(0.1)
        
        # Click 3: "Standard Center" - Fallback position
        click3_x = int(w * 0.18)
        click3_y = int(h * 0.45)
        print(f"   -> Click 3 (Standard): ({click3_x}, {click3_y})")
        pyautogui.click(click3_x, click3_y)
        time.sleep(1.5)
        
        # VERIFICATION
        try:
            active_window = gw.getActiveWindow()
            current_title = active_window.title if active_window else "Unknown"
        except:
            current_title = "Unknown"
        
        print(f"   ✅ Navigated. Current page: {current_title}")
        return f"Opened {site_name}."


def get_real_desktop_path():
    """
    Detects if the user is using OneDrive for Desktop and returns the correct path.
    """
    user_profile = os.environ.get('USERPROFILE')
    onedrive_desktop = os.path.join(user_profile, 'OneDrive', 'Desktop')
    
    if os.path.exists(onedrive_desktop):
        return onedrive_desktop
    else:
        return os.path.join(user_profile, 'Desktop')


def handle_file_ops(payload):
    """
    Handles file system operations: CREATE, DELETE.
    """
    operation = payload.get("operation")
    path_str = payload.get("path")
    
    # Expand environment variables (e.g. %USERPROFILE%)
    target_path = os.path.expandvars(path_str)
    
    # --- ONEDRIVE FIX ---
    user_profile = os.environ.get('USERPROFILE')
    standard_desktop = os.path.join(user_profile, 'Desktop')
    real_desktop = get_real_desktop_path()
    
    # If the path starts with the standard desktop but the real one is different (OneDrive)
    if target_path.startswith(standard_desktop) and standard_desktop != real_desktop:
        target_path = target_path.replace(standard_desktop, real_desktop, 1)
        print(f"📂 Redirecting to OneDrive Desktop: {target_path}")
    
    try:
        if operation == "CREATE":
            os.makedirs(target_path, exist_ok=True)
            if os.path.exists(target_path):
                # Auto-Open Feature: Open the new folder in Explorer
                subprocess.Popen(['explorer', target_path])
                
                # Force visibility
                folder_name = os.path.basename(target_path)
                force_foreground(folder_name)
                
                return f"Created and opened folder at {target_path}"
            else:
                return f"Failed to create folder at {target_path}"
                
        elif operation == "DELETE":
            if os.path.isdir(target_path):
                shutil.rmtree(target_path)
                return f"Deleted folder: {target_path}"
            elif os.path.isfile(target_path):
                os.remove(target_path)
                return f"Deleted file: {target_path}"
            else:
                return f"Path not found: {target_path}"
                
    except Exception as e:
        return f"File Op Error: {e}"
    
    return "Unknown File Operation"


def get_system_status():
    """
    Returns a professional system health report.
    """
    cpu = psutil.cpu_percent(interval=0.5)
    memory = psutil.virtual_memory().percent
    battery = psutil.sensors_battery()
    
    status = f"Systems nominal. CPU at {cpu}%. Memory usage at {memory}%."
    if battery:
        status += f" Battery level is {battery.percent}%."
        if battery.power_plugged:
            status += " Charging."
            
    return status


def take_screenshot(name_hint="screenshot"):
    """
    Takes a screenshot, saves it to Desktop, and opens it.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"Nova_Capture_{timestamp}.png"
    desktop = get_real_desktop_path()
    filepath = os.path.join(desktop, filename)
    
    # Capture
    screenshot = pyautogui.screenshot()
    screenshot.save(filepath)
    
    # Open
    subprocess.Popen(['explorer', filepath])
    return f"Screenshot saved to Desktop as {filename}"


def handle_protocol(protocol_name):
    """
    Executes complex multi-step macros using universal app launcher.
    """
    protocol = protocol_name.upper()
    
    if protocol == "CODING":
        # 1. Open VS Code via Start Menu
        launch_app("Visual Studio Code", wait_time=2.0)
        time.sleep(0.5)
        
        # 2. Open GitHub via browser
        launch_app("Brave", wait_time=2.0)
        time.sleep(0.5)
        browser_navigate("https://github.com")
        
        # 3. Play Lo-Fi
        play_music_on_spotify("lofi hip hop radio")
        
        return "Coding Protocol Initiated: VS Code, GitHub, and Lo-Fi ready."
        
    elif protocol == "SOCIAL":
        # Open Discord via Start Menu
        launch_app("Discord", wait_time=2.0)
        
        # Open WhatsApp (Web) via browser
        launch_app("Brave", wait_time=2.0)
        time.sleep(0.5)
        browser_navigate("https://web.whatsapp.com")
        
        return "Social Protocol Active."
        
    elif protocol == "GAMING":
        # Open Steam via Start Menu
        launch_app("Steam", wait_time=3.0)
        return "Gaming Mode Engaged. Steam launched."
        
    return f"Unknown Protocol: {protocol_name}"


# --- EXECUTION ENGINE ---
def execute_step(step):
    action = step.get("action")
    payload = step.get("payload")
    
    print(f"⚙️ EXEC: {action} -> {payload}")

    try:
        # 1. NATIVE SYSTEM APPS (Universal Launcher)
        if action == "LAUNCH_SYS":
            # Map common aliases to proper app names
            app_map = {
                "calc": "Calculator",
                "calculator": "Calculator",
                "notepad": "Notepad",
                "settings": "Settings",
                "ms-settings:": "Settings",
                "explorer": "File Explorer",
                "file explorer": "File Explorer",
            }
            
            # Get proper app name or use payload as-is
            app_name = app_map.get(payload.lower(), payload)
            
            # Use universal launcher
            launch_app(app_name, wait_time=1.5)
            return f"Opened {app_name}."

        # 2. FILE OPERATIONS
        elif action == "FILE_OPS":
            return handle_file_ops(payload)

        # 3. BROWSER CONTROL (Smart Search)
        elif action == "BROWSER":
            # Use Smart Website navigation (Google I'm Feeling Lucky)
            return open_smart_website(payload)

        # 4. MUSIC CONTROL (YouTube)
        elif action == "PLAY_MUSIC":
            return play_music_on_youtube(payload)

        # 5. WEB DOWNLOAD (Human-Like)
        elif action == "DOWNLOAD_WEB":
            return handle_web_download(payload)

        # 6. SHOWCASE MODULES
        elif action == "SYSTEM_CHECK":
            return get_system_status()
            
        elif action == "PROTOCOL":
            return handle_protocol(payload)
            
        elif action == "SCREENSHOT":
            return take_screenshot(payload)

        # 6. HUMAN INPUT SIMULATION
        elif action == "TYPE_STRING":
            time.sleep(0.5)  # Wait for window focus
            # Hacker Style Typing (Visible)
            pyautogui.write(payload, interval=0.05)
            return "Typed text."
            
        elif action == "PRESS_KEY":
            keys = payload.split('+')
            if len(keys) > 1:
                pyautogui.hotkey(*keys)
            else:
                pyautogui.press(keys[0])
            return f"Pressed {payload}."

        elif action == "RESPONSE":
            return payload
        
        # WINDOWS SHORTCUT INTELLIGENCE
        elif action == "WINDOWS_SHORTCUT":
            result = execute_windows_shortcut(payload)
            return result["description"]

    except Exception as e:
        return f"Error executing {action}: {e}"
        
    return "Action complete."

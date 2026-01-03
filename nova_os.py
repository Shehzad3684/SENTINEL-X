"""
Nova OS - The Execution Engine
High-speed GUI automation with instant clicks (no demo animations).
"""

import os
import time
import shutil
import subprocess
import pyautogui
import psutil
import datetime
import pygetwindow as gw


class NovaOS:
    """
    Operating System Interface for Nova.
    Provides primitives (press, write, mouse) and high-level macros.
    All clicks are INSTANT - no slow demo animations.
    """
    
    # --- KNOWLEDGE BASES ---
    KNOWN_SITES = {
        "olx": "olx.com.pk",
        "youtube": "youtube.com",
        "facebook": "facebook.com",
        "whatsapp": "web.whatsapp.com",
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
        "wikipedia": "wikipedia.org",
        "pinterest": "pinterest.com",
        "tiktok": "tiktok.com",
        "twitch": "twitch.tv",
        "discord": "discord.com",
    }
    
    DIRECT_URLS = {
        "vlc": "https://www.videolan.org/vlc/download-windows.html",
        "chrome": "https://www.google.com/chrome/",
        "steam": "https://store.steampowered.com/about/",
        "discord": "https://discord.com/download",
        "firefox": "https://www.mozilla.org/en-US/firefox/new/",
        "spotify": "https://www.spotify.com/download/windows/",
        "vscode": "https://code.visualstudio.com/download",
        "brave": "https://brave.com/download/",
        "zoom": "https://zoom.us/download",
        "obs": "https://obsproject.com/download",
        "git": "https://git-scm.com/download/win",
        "python": "https://www.python.org/downloads/",
        "nodejs": "https://nodejs.org/en/download/",
        "7zip": "https://www.7-zip.org/download.html",
        "winrar": "https://www.win-rar.com/download.html",
        "notepad++": "https://notepad-plus-plus.org/downloads/",
        "audacity": "https://www.audacityteam.org/download/",
        "gimp": "https://www.gimp.org/downloads/",
        "blender": "https://www.blender.org/download/",
    }
    
    APP_ALIASES = {
        "calc": "Calculator",
        "calculator": "Calculator",
        "notepad": "Notepad",
        "settings": "Settings",
        "explorer": "File Explorer",
    }
    
    def __init__(self):
        """Initialize the OS interface."""
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"🖥️ NovaOS initialized. Screen: {self.screen_width}x{self.screen_height}")
    
    # ==================== BASE PRIMITIVES ====================
    
    def press(self, *keys):
        """Press key(s). Instant."""
        pyautogui.hotkey(*keys)
    
    def write(self, text, interval=0.0):
        """Type text. Instant by default."""
        pyautogui.write(text, interval=interval)
    
    def mouse(self, x_pct, y_pct):
        """
        Click at percentage coordinates. INSTANT (no animation).
        x_pct, y_pct are floats between 0.0 and 1.0.
        """
        x = int(self.screen_width * x_pct)
        y = int(self.screen_height * y_pct)
        pyautogui.click(x, y)
        return x, y
    
    def wait(self, seconds):
        """Wait for specified seconds."""
        time.sleep(seconds)
    
    # ==================== FOCUS UTILITIES ====================
    
    def focus_anchor(self):
        """Click center of screen to guarantee OS focus."""
        x, y = self.mouse(0.5, 0.5)
        print(f"   -> Focus Anchor: ({x}, {y})")
        self.wait(0.3)
    
    def smart_maximize(self, app_name):
        """Only maximize if window is not already maximized."""
        try:
            windows = gw.getWindowsWithTitle(app_name)
            if windows:
                win = windows[0]
                if not win.isMaximized:
                    print(f"   -> Maximizing '{app_name}'...")
                    try:
                        win.maximize()
                        self.wait(0.5)
                    except:
                        self.press('win', 'up')
                        self.wait(0.5)
                else:
                    print(f"   -> Already maximized.")
            else:
                self.press('win', 'up')
                self.wait(0.5)
        except Exception as e:
            print(f"   -> Maximize fallback: {e}")
            self.press('win', 'up')
            self.wait(0.5)
    
    # ==================== HIGH-LEVEL MACROS ====================
    
    def launch_app(self, app_name):
        """
        Universal App Launcher via Start Menu.
        Includes Focus Anchor and Smart Maximize.
        """
        # Resolve aliases
        resolved_name = self.APP_ALIASES.get(app_name.lower(), app_name)
        print(f"🚀 LAUNCH: '{resolved_name}'")
        
        # Win -> Type -> Enter
        self.press('win')
        self.wait(0.3)
        self.write(resolved_name, interval=0.05)
        self.wait(0.3)
        self.press('enter')
        
        # Wait for window
        print(f"   -> Waiting for window (2.0s)...")
        self.wait(2.0)
        
        # Focus Anchor + Maximize
        self.focus_anchor()
        self.smart_maximize(resolved_name)
        
        print(f"   ✅ '{resolved_name}' ready.")
        return True
    
    def play_youtube(self, song_name):
        """
        One-Shot YouTube: Launch -> URL -> DENSE GRID Click.
        Dense Grid: 5 clicks in thumbnail zone - ONE WILL HIT.
        """
        print(f"🎵 YOUTUBE: '{song_name}'")
        
        if len(song_name) < 2:
            return "Song name too short."
        
        # Launch Brave
        self.launch_app("Brave")
        
        # Focus address bar
        self.press('ctrl', 'l')
        self.wait(0.3)
        
        # Navigate to YouTube search
        query = song_name.replace(' ', '+')
        url = f"https://www.youtube.com/results?search_query={query}"
        print(f"   -> URL: {url}")
        self.write(url, interval=0.01)
        self.wait(0.1)
        self.press('enter')
        
        # Wait for results
        print("   -> Waiting for YouTube (3.5s)...")
        self.wait(3.5)
        
        # THE DENSE GRID STRATEGY - 5 clicks, one WILL hit
        w, h = self.screen_width, self.screen_height
        print(f"   -> Screen: {w}x{h}")
        print("   -> 🎯 DENSE GRID: Executing 5-point strike pattern...")
        
        # Grid points in the thumbnail zone
        grid_points = [
            (0.35, 0.38, "Sweet Spot"),      # Center of first thumbnail
            (0.25, 0.38, "Left Safety"),     # Left side of thumbnail
            (0.45, 0.38, "Right Safety"),    # Right side of thumbnail
            (0.35, 0.30, "High Safety"),     # Above (avoids description)
            (0.35, 0.45, "Low Safety"),      # Below (avoids banner)
        ]
        
        for x_pct, y_pct, label in grid_points:
            click_x = int(w * x_pct)
            click_y = int(h * y_pct)
            print(f"      -> {label}: ({click_x}, {click_y})")
            pyautogui.click(click_x, click_y)
            self.wait(0.1)  # Brief pause between clicks
        
        print(f"   ✅ Playing '{song_name}'")
        return f"Playing '{song_name}' on YouTube."
        return f"Playing '{song_name}' on YouTube."
    
    def smart_browse(self, site_name):
        """
        Smart Website Navigation.
        Known sites -> Direct URL. Unknown -> Google + Scatter Click.
        """
        print(f"🌐 BROWSE: '{site_name}'")
        
        # Launch Brave
        self.launch_app("Brave")
        
        # Focus address bar
        self.press('ctrl', 'l')
        self.wait(0.3)
        
        # Check knowledge base
        site_key = site_name.lower().replace(" ", "").strip()
        
        if site_key in self.KNOWN_SITES:
            # KNOWN - Direct URL
            direct_url = self.KNOWN_SITES[site_key]
            print(f"   -> 🧠 KNOWN: {direct_url}")
            self.write(direct_url, interval=0.02)
            self.wait(0.1)
            self.press('enter')
            self.wait(2.0)
            print(f"   ✅ Opened {site_name} directly.")
            return f"Opening {site_name} directly."
        
        else:
            # UNKNOWN - Google Search + Scatter Click
            print(f"   -> 🔍 UNKNOWN: Google search...")
            self.write(site_name, interval=0.03)
            self.wait(0.2)
            self.press('enter')
            
            print(f"   -> Waiting for Google (3.5s)...")
            self.wait(3.5)
            
            # Calibrated Scatter: Low -> Right Panel -> Mid
            print(f"   -> Scatter Click (Low/Panel/Mid)...")
            self.mouse(0.18, 0.55)  # Safe Low
            self.wait(0.1)
            self.mouse(0.85, 0.35)  # Knowledge Panel
            self.wait(0.1)
            self.mouse(0.18, 0.45)  # Standard
            self.wait(1.5)
            
            print(f"   ✅ Navigated to {site_name}.")
            return f"Opened {site_name}."
    
    def download_file(self, app_name):
        """
        Download via Ctrl+F -> Esc -> Enter sequence.
        """
        print(f"📥 DOWNLOAD: '{app_name}'")
        
        app_key = app_name.lower().strip()
        
        # Navigate to download page
        if app_key in self.DIRECT_URLS:
            target_url = self.DIRECT_URLS[app_key]
            print(f"   -> Known URL: {target_url}")
            self.launch_app("Brave")
            self.press('ctrl', 'l')
            self.wait(0.3)
            self.write(target_url, interval=0.01)
            self.press('enter')
        else:
            search_query = f"{app_name} download"
            print(f"   -> Searching: '{search_query}'")
            self.smart_browse(search_query)
        
        # Wait for page load
        print(f"   -> Waiting for page (4.5s)...")
        self.wait(4.5)
        
        # Find & Click Protocol
        print(f"   -> Find & Click...")
        self.press('ctrl', 'f')
        self.wait(0.3)
        self.write("Download", interval=0.03)
        self.wait(0.2)
        self.press('enter')
        self.wait(0.3)
        
        # CRITICAL: Esc closes Find Bar, returns focus to element
        print(f"   -> Esc (close Find Bar)...")
        self.press('escape')
        self.wait(0.5)
        
        # Click the highlighted element
        print(f"   -> Enter (click button)...")
        self.press('enter')
        self.wait(1.0)
        
        print(f"   ✅ Download triggered for '{app_name}'.")
        return f"Download triggered for {app_name}."
    
    # ==================== SYSTEM UTILITIES ====================
    
    def get_system_status(self):
        """Get CPU, memory, and battery status."""
        cpu = psutil.cpu_percent(interval=0.5)
        memory = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        
        status = f"CPU: {cpu}%. Memory: {memory}%."
        if battery:
            status += f" Battery: {battery.percent}%."
            if battery.power_plugged:
                status += " Charging."
        
        return status
    
    def take_screenshot(self):
        """Take screenshot and save to Desktop."""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"Nova_Capture_{timestamp}.png"
        desktop = self._get_desktop_path()
        filepath = os.path.join(desktop, filename)
        
        screenshot = pyautogui.screenshot()
        screenshot.save(filepath)
        subprocess.Popen(['explorer', filepath])
        
        return f"Screenshot saved: {filename}"
    
    def handle_file_ops(self, operation, path):
        """Handle file/folder create/delete."""
        target_path = os.path.expandvars(path)
        
        # OneDrive fix
        user_profile = os.environ.get('USERPROFILE')
        standard_desktop = os.path.join(user_profile, 'Desktop')
        real_desktop = self._get_desktop_path()
        
        if target_path.startswith(standard_desktop) and standard_desktop != real_desktop:
            target_path = target_path.replace(standard_desktop, real_desktop, 1)
        
        try:
            if operation == "CREATE":
                os.makedirs(target_path, exist_ok=True)
                subprocess.Popen(['explorer', target_path])
                return f"Created: {target_path}"
            elif operation == "DELETE":
                if os.path.isdir(target_path):
                    shutil.rmtree(target_path)
                elif os.path.isfile(target_path):
                    os.remove(target_path)
                return f"Deleted: {target_path}"
        except Exception as e:
            return f"Error: {e}"
        
        return "Unknown operation."
    
    def type_string(self, text):
        """Type text with visible effect."""
        self.wait(0.5)
        self.write(text, interval=0.05)
        return "Typed text."
    
    def press_key(self, key_combo):
        """Press key combination (e.g., 'ctrl+c')."""
        keys = key_combo.split('+')
        self.press(*keys)
        return f"Pressed {key_combo}."
    
    def _get_desktop_path(self):
        """Get real desktop path (handles OneDrive)."""
        user_profile = os.environ.get('USERPROFILE')
        onedrive_desktop = os.path.join(user_profile, 'OneDrive', 'Desktop')
        
        if os.path.exists(onedrive_desktop):
            return onedrive_desktop
        return os.path.join(user_profile, 'Desktop')
    
    # ==================== PROTOCOLS ====================
    
    def handle_protocol(self, protocol_name):
        """Multi-app macro protocols."""
        proto = protocol_name.upper()
        
        if proto == "CODING":
            self.launch_app("Visual Studio Code")
            self.launch_app("Terminal")
            self.smart_browse("stackoverflow")
            return "Coding Protocol Initiated."
        
        elif proto == "SOCIAL":
            self.smart_browse("twitter")
            self.wait(2)
            self.smart_browse("instagram")
            self.wait(2)
            self.smart_browse("facebook")
            return "Social Protocol Initiated."
        
        elif proto == "GAMING":
            self.launch_app("Steam")
            self.smart_browse("twitch")
            return "Gaming Protocol Initiated."
        
        return f"Unknown protocol: {protocol_name}"
    
    # ==================== EXECUTION ENGINE ====================
    
    def execute_step(self, step):
        """
        Execute a single step from the Nova plan.
        Drop-in replacement for nova_actions.execute_step()
        """
        action = step.get("action")
        payload = step.get("payload")
        
        print(f"⚙️ EXEC: {action} -> {payload}")
        
        try:
            # 1. NATIVE SYSTEM APPS (Universal Launcher)
            if action == "LAUNCH_SYS":
                self.launch_app(payload)
                return f"Opened {payload}."
            
            # 2. FILE OPERATIONS
            elif action == "FILE_OPS":
                op = payload.get("operation")
                path = payload.get("path")
                return self.handle_file_ops(op, path)
            
            # 3. BROWSER CONTROL (Smart Search)
            elif action == "BROWSER":
                return self.smart_browse(payload)
            
            # 4. MUSIC CONTROL (YouTube)
            elif action == "PLAY_MUSIC":
                return self.play_youtube(payload)
            
            # 5. WEB DOWNLOAD (Human-Like)
            elif action == "DOWNLOAD_WEB":
                return self.download_file(payload)
            
            # 6. SYSTEM CHECK
            elif action == "SYSTEM_CHECK":
                return self.get_system_status()
            
            # 7. PROTOCOL
            elif action == "PROTOCOL":
                return self.handle_protocol(payload)
            
            # 8. SCREENSHOT
            elif action == "SCREENSHOT":
                return self.take_screenshot()
            
            # 9. TYPE STRING
            elif action == "TYPE_STRING":
                return self.type_string(payload)
            
            # 10. PRESS KEY
            elif action == "PRESS_KEY":
                return self.press_key(payload)
            
            # 11. RESPONSE (just return it)
            elif action == "RESPONSE":
                return payload
            
        except Exception as e:
            return f"Error executing {action}: {e}"
        
        return "Action complete."


# --- MODULE-LEVEL INSTANCE (for backward compatibility) ---
_nova_os = NovaOS()

def execute_step(step):
    """Module-level function for backward compatibility with main.py."""
    return _nova_os.execute_step(step)

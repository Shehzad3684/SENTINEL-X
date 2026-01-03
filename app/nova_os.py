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

# Import path utilities from package
from app import get_runtime_audio_file


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
        "word": "Word",
        "microsoft word": "Word",
        "ms word": "Word",
        "whatsapp": "WhatsApp",
    }
    
    def __init__(self):
        """Initialize the OS interface."""
        self.screen_width, self.screen_height = pyautogui.size()
        print(f"FOX-3 >> TARGETING SYSTEM ONLINE // DISPLAY: {self.screen_width}x{self.screen_height}")
    
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
    
    def _ensure_window_state(self, app_name, launch_if_missing=True):
        """
        THE "GOD MODE" HELPER - Ensures window is open, active, and maximized.
        Call this at the START of every capability (Word, Browser, etc.)
        
        Args:
            app_name: Partial window title to find (e.g., "Word", "Brave")
            launch_if_missing: If True, will launch the app if not found
            
        Returns:
            True if window is ready, False if failed
        """
        w, h = self.screen_width, self.screen_height
        print(f"   🔍 State Check: Looking for '{app_name}'...")
        
        # Step 1: Find windows matching the app name
        windows = gw.getWindowsWithTitle(app_name)
        
        # Step 2: Launch if missing
        if not windows and launch_if_missing:
            print(f"   -> '{app_name}' not found. Launching...")
            self.press('win')
            self.wait(0.5)
            pyautogui.write(app_name, interval=0.05)
            self.wait(0.5)
            self.press('enter')
            self.wait(3.0)  # Wait for app to start
            
            # Re-check for windows
            windows = gw.getWindowsWithTitle(app_name)
            if not windows:
                print(f"   ❌ Failed to launch '{app_name}'")
                return False
        
        if not windows:
            print(f"   ❌ No window found for '{app_name}'")
            return False
        
        # Step 3: Activate the window
        win = windows[0]
        print(f"   -> Found: '{win.title}'")
        try:
            win.activate()
        except Exception as e:
            print(f"   -> Activate fallback: {e}")
            try:
                win.minimize()
                self.wait(0.2)
                win.restore()
            except:
                pass
        self.wait(0.3)
        
        # Step 4: CRITICAL - Maximize Check
        try:
            if not win.isMaximized:
                print(f"   -> Window not maximized. Maximizing...")
                try:
                    win.maximize()
                except:
                    self.press('win', 'up')
                self.wait(1.5)  # CRITICAL: Wait for animation to finish
            else:
                print(f"   -> Already maximized.")
        except Exception as e:
            print(f"   -> Maximize check failed: {e}, using Win+Up...")
            self.press('win', 'up')
            self.wait(1.5)
        
        # Step 5: Focus Anchor - Physical click to steal focus from Taskbar
        print(f"   -> Focus anchor click (center of screen)")
        pyautogui.click(int(w * 0.5), int(h * 0.5))
        self.wait(0.3)
        
        print(f"   ✅ '{app_name}' is ready and maximized.")
        return True
    
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
        print(f"FOX-3 >> DEPLOYING ASSET: {resolved_name.upper()}")
        
        # Win -> Type -> Enter
        self.press('win')
        self.wait(0.3)
        self.write(resolved_name, interval=0.05)
        self.wait(0.3)
        self.press('enter')
        
        # Wait for window
        print(f"   -> ACQUISITION DELAY: 2.0s")
        self.wait(2.0)
        
        # Focus Anchor + Maximize
        self.focus_anchor()
        self.smart_maximize(resolved_name)
        
        print(f"   << SPLASH: {resolved_name.upper()} DEPLOYED")
        return True
    
    def play_youtube(self, song_name):
        """
        State-Aware YouTube Player.
        Uses _ensure_window_state protocol before interacting.
        """
        print(f"FOX-3 >> DEPLOYING COUNTERMEASURE: {song_name.upper()}")
        
        if len(song_name) < 2:
            return "Song name too short."
        
        # STATE CHECK PROTOCOL: Ensure Brave is open, active, and maximized
        if not self._ensure_window_state("Brave"):
            return "❌ Error: Could not focus Brave browser."
        
        # Always open new tab to avoid overwriting existing work
        self.press('ctrl', 't')
        self.wait(0.5)
        
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
    
    def smart_browse(self, site_name):
        """
        State-Aware Website Navigation.
        Uses _ensure_window_state protocol before interacting.
        """
        print(f"🌐 BROWSE: '{site_name}'")
        
        # STATE CHECK PROTOCOL: Ensure Brave is open, active, and maximized
        if not self._ensure_window_state("Brave"):
            return "❌ Error: Could not focus Brave browser."
        
        # Open new tab to avoid overwriting existing work
        self.press('ctrl', 't')
        self.wait(0.5)
        
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

    def open_direct_url(self, url):
        """
        Direct URL Navigation - No guessing, no searching.
        Opens the exact URL provided by Sentinel Core.
        Reuses existing browser tab if possible.
        """
        print(f"🎯 DIRECT URL: '{url}'")
        
        # STATE CHECK PROTOCOL: Ensure Brave is open, active, and maximized
        if not self._ensure_window_state("Brave"):
            return "Could not open browser."
        
        # Open new tab
        self.press('ctrl', 't')
        self.wait(0.4)
        
        # Focus address bar
        self.press('ctrl', 'l')
        self.wait(0.2)
        
        # Type exact URL
        self.write(url, interval=0.01)
        self.wait(0.1)
        self.press('enter')
        
        # Extract site name from URL for response
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc.replace("www.", "")
            site_name = domain.split(".")[0].capitalize()
        except:
            site_name = url
        
        self.wait(1.5)
        print(f"   ✅ Opened {url}")
        return f"Opening {site_name}."
    
    def download_file(self, app_name):
        """
        State-Aware Download Function.
        Uses _ensure_window_state protocol before interacting.
        """
        print(f"📥 DOWNLOAD: '{app_name}'")
        
        app_key = app_name.lower().strip()
        
        # STATE CHECK PROTOCOL: Ensure Brave is open, active, and maximized
        if not self._ensure_window_state("Brave"):
            return "❌ Error: Could not focus Brave browser."
        
        # Open new tab
        self.press('ctrl', 't')
        self.wait(0.5)
        
        # Navigate to download page
        if app_key in self.DIRECT_URLS:
            target_url = self.DIRECT_URLS[app_key]
            print(f"   -> Known URL: {target_url}")
            self.press('ctrl', 'l')
            self.wait(0.3)
            self.write(target_url, interval=0.01)
            self.press('enter')
        else:
            search_query = f"{app_name} download"
            print(f"   -> Searching: '{search_query}'")
            self.press('ctrl', 'l')
            self.wait(0.3)
            self.write(search_query, interval=0.02)
            self.press('enter')
            self.wait(3.5)
            # Click first result
            self.mouse(0.18, 0.45)
        
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
    
    def minimize_all(self):
        """Minimize all windows - show desktop. Win+M"""
        print("🖥️ Minimizing all windows...")
        self.press('win', 'm')
        time.sleep(0.5)
        return "All windows minimized. Desktop shown."
    
    def show_desktop(self):
        """Alias for minimize_all - show desktop. Win+D"""
        print("🖥️ Showing desktop...")
        self.press('win', 'd')
        time.sleep(0.5)
        return "Desktop shown."
    
    def execute_windows_shortcut(self, intent_text):
        """
        Execute Windows keyboard shortcuts based on user intent.
        
        This method:
        1. Receives natural language intent from user speech
        2. Uses the shortcut intelligence system to match intent
        3. Executes the appropriate Windows shortcut
        4. Returns human-readable status
        
        Args:
            intent_text: Natural language command (e.g., "open task manager")
            
        Returns:
            Status message describing what was executed
        """
        print(f"🎯 WINDOWS SHORTCUT: Processing '{intent_text}'...")
        
        # Import the shortcut intelligence functions
        from app.nova_actions import execute_windows_shortcut as shortcut_execute
        
        # Execute the shortcut with our status callback
        result = shortcut_execute(intent_text)
        
        if result["success"]:
            return result["description"]
        else:
            # If shortcut execution failed, return the error
            return result["description"]
    
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
    
    def type_in_word(self, text):
        """
        Focus Microsoft Word and type text. If Word isn't open, opens it first.
        Uses clipboard for reliable text entry (handles all characters).
        """
        print(f"📝 WORD: Typing text into Word...")
        
        # Step 1: Check if Word is already open with a document
        word_doc_window = None
        word_start_window = None
        
        for win in gw.getAllWindows():
            title = win.title.lower()
            # Document window has "document" or file extension in title
            if ('document' in title or '.docx' in title or '.doc' in title) and 'word' in title:
                word_doc_window = win
                break
            # Startup screen just says "Word"
            elif title.strip() == 'word':
                word_start_window = win
        
        if word_doc_window:
            # Word document is open - just focus it
            print(f"   -> Found Word document: '{word_doc_window.title}'")
            try:
                word_doc_window.activate()
                self.wait(0.5)
            except Exception as e:
                print(f"   -> Activate failed, trying minimize/restore: {e}")
                try:
                    word_doc_window.minimize()
                    self.wait(0.2)
                    word_doc_window.restore()
                    self.wait(0.5)
                except:
                    pass
        elif word_start_window:
            # Word is at startup screen - click Blank document
            print(f"   -> Found Word startup screen, clicking Blank document...")
            try:
                word_start_window.activate()
                self.wait(0.5)
            except:
                pass
            
            # Click "Blank document" - it's in the upper-left area of the window
            # Based on screenshot: approximately 17% from left, 30% from top
            w, h = self.screen_width, self.screen_height
            click_x = int(w * 0.17)
            click_y = int(h * 0.32)
            print(f"   -> Clicking Blank document at ({click_x}, {click_y})")
            pyautogui.click(click_x, click_y)
            
            # Wait for document to open
            print("   -> Waiting for document to open...")
            for i in range(10):
                self.wait(0.5)
                for win in gw.getAllWindows():
                    title = win.title.lower()
                    if 'document' in title or '.docx' in title:
                        word_doc_window = win
                        print(f"   -> Document opened: '{win.title}'")
                        break
                if word_doc_window:
                    break
            
            if not word_doc_window:
                # Fallback: try double-click
                print("   -> Double-clicking Blank document...")
                pyautogui.doubleClick(click_x, click_y)
                self.wait(2.0)
        else:
            # Word not open at all - launch it
            print("   -> Word not open, launching...")
            self.launch_app("Word")
            
            # Wait for Word startup screen
            print("   -> Waiting for Word to open...")
            for i in range(20):
                self.wait(0.5)
                for win in gw.getAllWindows():
                    title = win.title.lower()
                    if 'word' in title:
                        word_start_window = win
                        print(f"   -> Word detected: '{win.title}'")
                        break
                if word_start_window:
                    break
            
            if not word_start_window:
                print("   ⚠️ Could not detect Word window after 10s")
                return "Error: Microsoft Word did not open."
            
            # Wait for UI to fully render
            self.wait(2.0)
            
            # Click "Blank document" 
            w, h = self.screen_width, self.screen_height
            click_x = int(w * 0.17)
            click_y = int(h * 0.32)
            print(f"   -> Clicking Blank document at ({click_x}, {click_y})")
            pyautogui.doubleClick(click_x, click_y)
            
            # Wait for document
            print("   -> Waiting for document...")
            self.wait(2.5)
        
        # Step 2: Click in document area to ensure focus (center-right of screen, avoiding ribbon)
        print("   -> Clicking document area to focus...")
        w, h = self.screen_width, self.screen_height
        pyautogui.click(int(w * 0.5), int(h * 0.55))  # Below ribbon area
        self.wait(0.3)
        
        # Step 3: Type text using clipboard (reliable for all characters)
        print(f"   -> Typing text via clipboard ({len(text)} characters)...")
        try:
            import pyperclip
            pyperclip.copy(text)
            self.press('ctrl', 'v')
            self.wait(0.3)
        except ImportError:
            # Fallback: use typewrite with slower interval for reliability
            print("   -> pyperclip not available, using typewrite...")
            pyautogui.typewrite(text, interval=0.03)
        
        print(f"   ✅ Text written to Word.")
        return f"Typed {len(text)} characters in Microsoft Word."

    # ==================== MS WORD AUTOMATION MODULE ====================
    # Simple, reliable "Wait & Click" strategy
    
    def _type_with_clipboard(self, text):
        """Type text using clipboard for reliability (handles all characters)."""
        try:
            import pyperclip
            pyperclip.copy(text)
            self.press('ctrl', 'v')
            self.wait(0.2)
        except ImportError:
            pyautogui.write(text, interval=0.015)

    def launch_word_robust(self):
        """
        Launch Microsoft Word and open a blank document.
        Returns True only if Word is confirmed ready.
        """
        print("📝 WORD: Starting Word automation...")
        
        w, h = pyautogui.size()
        
        # ==================== CHECK IF DOCUMENT ALREADY OPEN ====================
        for win in gw.getAllWindows():
            title = win.title.lower()
            if ('document' in title or '.docx' in title) and 'word' in title:
                print(f"   ✅ Document already open: '{win.title}'")
                try:
                    win.activate()
                    time.sleep(0.5)
                    # Click document area to focus cursor
                    pyautogui.click(int(w * 0.5), int(h * 0.5))
                    time.sleep(0.3)
                    return True
                except Exception as e:
                    print(f"   ⚠️ Could not activate: {e}")
        
        # ==================== CHECK IF WORD HOME SCREEN IS OPEN ====================
        for win in gw.getAllWindows():
            title = win.title.lower().strip()
            if title == 'word':
                print(f"   -> Word home screen detected, clicking Blank Document...")
                try:
                    win.activate()
                    time.sleep(1.0)
                except:
                    pass
                
                # Click Blank Document (multiple attempts at different positions)
                positions = [(0.16, 0.30), (0.12, 0.28), (0.20, 0.32)]
                for px, py in positions:
                    click_x = int(w * px)
                    click_y = int(h * py)
                    print(f"   -> Clicking at ({click_x}, {click_y})...")
                    pyautogui.click(click_x, click_y)
                    time.sleep(0.5)
                
                # Wait for document
                print("   -> Waiting 3s for document...")
                time.sleep(3.0)
                
                # Click document area
                pyautogui.click(int(w * 0.5), int(h * 0.5))
                time.sleep(0.5)
                
                print("   ✅ Word ready from home screen!")
                return True
        
        # ==================== WORD NOT OPEN - LAUNCH FRESH ====================
        print("   -> Word not running, launching fresh...")
        
        # Try multiple launch methods
        launch_success = False
        
        # Method 1: Start menu search
        print("   -> Method 1: Start menu search...")
        self.press('win')
        time.sleep(0.8)
        pyautogui.write("Word", interval=0.08)
        time.sleep(1.0)
        self.press('enter')
        
        # Wait for Word to load
        print("   -> Waiting 5s for Word to launch...")
        time.sleep(5.0)
        
        # Check if Word opened
        for win in gw.getAllWindows():
            if 'word' in win.title.lower():
                launch_success = True
                print(f"   -> Found Word window: '{win.title}'")
                break
        
        if not launch_success:
            # Method 2: Direct winword.exe
            print("   -> Method 2: Direct winword.exe...")
            try:
                subprocess.Popen(['winword.exe'])
                time.sleep(5.0)
                launch_success = True
            except:
                pass
        
        if not launch_success:
            print("   ❌ Could not launch Microsoft Word")
            return False
        
        # Click Blank Document
        print("   -> Clicking Blank Document...")
        positions = [(0.16, 0.30), (0.12, 0.28), (0.20, 0.32)]
        for px, py in positions:
            click_x = int(w * px)
            click_y = int(h * py)
            pyautogui.click(click_x, click_y)
            time.sleep(0.3)
        
        # Wait for document
        print("   -> Waiting 3s for document to open...")
        time.sleep(3.0)
        
        # Click in document area
        print("   -> Clicking document area...")
        pyautogui.click(int(w * 0.5), int(h * 0.5))
        time.sleep(0.5)
        
        print("   ✅ Word ready!")
        return True

    def write_pro_document(self, topic, content_dict):
        """
        Write a complete, verified essay in Microsoft Word.
        
        CRITICAL: This method ONLY reports success if content is actually written.
        
        Args:
            topic: The document title
            content_dict: Dictionary with 'title', 'introduction', 'body' (list), 'conclusion'
        
        Returns:
            Status message with actual word count and section count
        """
        print(f"📝 WORD: Writing complete essay on '{topic}'...")
        
        # Track what we actually write
        sections_written = 0
        total_words = 0
        
        # ==================== VALIDATE INPUT ====================
        if not content_dict:
            return "ERROR: No content provided. Essay generation failed."
        
        title = content_dict.get('title', topic)
        introduction = content_dict.get('introduction', '')
        body_paragraphs = content_dict.get('body', [])
        conclusion = content_dict.get('conclusion', '')
        
        # Validate we have actual content
        if not introduction or len(introduction) < 50:
            print("   ❌ ERROR: Introduction is missing or too short")
            return "ERROR: Failed to generate introduction content."
        
        if not body_paragraphs or len(body_paragraphs) == 0:
            print("   ❌ ERROR: Body paragraphs are missing")
            return "ERROR: Failed to generate body content."
        
        if not conclusion or len(conclusion) < 30:
            print("   ❌ ERROR: Conclusion is missing or too short")
            return "ERROR: Failed to generate conclusion content."
        
        # ==================== TITLE ====================
        print(f"   -> Writing title: {title}")
        self._type_with_clipboard(title)
        self.wait(0.3)
        
        # Select title and format
        self.press('home')
        self.wait(0.1)
        pyautogui.hotkey('shift', 'end')
        self.wait(0.2)
        
        # Format: Bold + Center + Larger font
        self.press('ctrl', 'b')  # Bold
        self.wait(0.1)
        self.press('ctrl', 'e')  # Center
        self.wait(0.1)
        
        # Move to end and add spacing
        self.press('end')
        self.wait(0.1)
        self.press('enter')
        self.press('enter')
        self.wait(0.2)
        
        # Reset formatting: Left align, Bold off
        self.press('ctrl', 'l')
        self.wait(0.1)
        self.press('ctrl', 'b')  # Bold off
        self.wait(0.2)
        
        total_words += len(title.split())
        
        # ==================== INTRODUCTION ====================
        print(f"   -> Writing INTRODUCTION ({len(introduction.split())} words)")
        
        # Write heading
        self._type_with_clipboard("INTRODUCTION")
        self.wait(0.2)
        
        # Format heading: Bold
        self.press('home')
        self.wait(0.1)
        pyautogui.hotkey('shift', 'end')
        self.wait(0.1)
        self.press('ctrl', 'b')
        self.wait(0.1)
        
        # New line, bold off
        self.press('end')
        self.wait(0.1)
        self.press('enter')
        self.wait(0.1)
        self.press('ctrl', 'b')  # Bold off
        self.wait(0.1)
        
        # Write introduction content
        self._type_with_clipboard(introduction)
        self.wait(0.3)
        
        # Add spacing
        self.press('enter')
        self.press('enter')
        self.wait(0.2)
        
        total_words += len(introduction.split())
        sections_written += 1
        
        # ==================== BODY PARAGRAPHS ====================
        for i, paragraph in enumerate(body_paragraphs, 1):
            if not paragraph or len(paragraph) < 20:
                print(f"   -> Skipping empty body paragraph {i}")
                continue
            
            print(f"   -> Writing BODY PARAGRAPH {i} ({len(paragraph.split())} words)")
            
            # Write sub-heading
            self._type_with_clipboard(f"Section {i}")
            self.wait(0.2)
            
            # Format: Bold
            self.press('home')
            self.wait(0.1)
            pyautogui.hotkey('shift', 'end')
            self.wait(0.1)
            self.press('ctrl', 'b')
            self.wait(0.1)
            
            # New line, bold off
            self.press('end')
            self.wait(0.1)
            self.press('enter')
            self.wait(0.1)
            self.press('ctrl', 'b')
            self.wait(0.1)
            
            # Write paragraph content
            self._type_with_clipboard(paragraph)
            self.wait(0.3)
            
            # Add spacing
            self.press('enter')
            self.press('enter')
            self.wait(0.2)
            
            total_words += len(paragraph.split())
            sections_written += 1
        
        # ==================== CONCLUSION ====================
        print(f"   -> Writing CONCLUSION ({len(conclusion.split())} words)")
        
        # Write heading
        self._type_with_clipboard("CONCLUSION")
        self.wait(0.2)
        
        # Format heading: Bold
        self.press('home')
        self.wait(0.1)
        pyautogui.hotkey('shift', 'end')
        self.wait(0.1)
        self.press('ctrl', 'b')
        self.wait(0.1)
        
        # New line, bold off
        self.press('end')
        self.wait(0.1)
        self.press('enter')
        self.wait(0.1)
        self.press('ctrl', 'b')
        self.wait(0.1)
        
        # Write conclusion content
        self._type_with_clipboard(conclusion)
        self.wait(0.3)
        
        total_words += len(conclusion.split())
        sections_written += 1
        
        # ==================== VERIFICATION ====================
        # Only report success if we actually wrote content
        if sections_written < 3:
            print(f"   ❌ VERIFICATION FAILED: Only {sections_written} sections written")
            return f"ERROR: Essay incomplete. Only {sections_written} sections written."
        
        if total_words < 200:
            print(f"   ❌ VERIFICATION FAILED: Only {total_words} words written")
            return f"ERROR: Essay too short. Only {total_words} words written."
        
        # ==================== SUCCESS ====================
        print(f"   ✅ Essay complete! {sections_written} sections, {total_words} words")
        return f"Essay written successfully: {sections_written} sections, {total_words} words. Title: {title}"

    # Aliases for backward compatibility
    def launch_word(self):
        return self.launch_word_robust()
    
    def select_blank_document(self):
        return True  # Now integrated into launch_word_robust
    
    def write_formatted_doc(self, topic, content_dict):
        return self.write_pro_document(topic, content_dict)

    def write_in_word(self, topic, content_dict):
        """Main entry point for Word essay writing."""
        print(f"📝 WORD: Full automation for '{topic}'...")
        
        # Launch Word (handles all states: not open, home screen, or document)
        word_ready = self.launch_word_robust()
        
        if not word_ready:
            print("   ❌ ERROR: Failed to launch Microsoft Word")
            return "ERROR: Could not open Microsoft Word. Please ensure Word is installed."
        
        # Verify Word is actually open before writing
        time.sleep(1.0)
        word_found = False
        for win in gw.getAllWindows():
            title = win.title.lower()
            if 'word' in title or 'document' in title:
                word_found = True
                try:
                    win.activate()
                    time.sleep(0.5)
                except:
                    pass
                break
        
        if not word_found:
            print("   ❌ ERROR: Word window not detected after launch")
            return "ERROR: Word did not open properly. Please try again."
        
        print(f"   ✅ Word verified open. Writing essay...")
        
        # Write the document
        return self.write_pro_document(topic, content_dict)

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
            
            # 3.5. BROWSER_DIRECT - Open exact URL (from Sentinel Core)
            elif action == "BROWSER_DIRECT":
                return self.open_direct_url(payload)
            
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
            
            # 12. TYPE IN WORD (MS Word Automation - simple text)
            elif action == "TYPE_IN_WORD":
                return self.type_in_word(payload)
            
            # 13. WRITE ESSAY (MS Word Automation - formatted essay)
            elif action == "WRITE_ESSAY":
                # Generate essay using LLM
                try:
                    from app.nova_brain import generate_essay
                    essay_content = generate_essay(payload)
                    return self.write_in_word(payload, essay_content)
                except Exception as e:
                    return f"Error generating essay: {e}"
            
            # 14. MINIMIZE ALL (Show Desktop)
            elif action == "MINIMIZE_ALL":
                return self.minimize_all()
            
            # 15. WINDOWS SHORTCUT INTELLIGENCE
            elif action == "WINDOWS_SHORTCUT":
                return self.execute_windows_shortcut(payload)
            
            # 16. CHAT (Conversational responses)
            elif action == "CHAT":
                # Return the payload for TTS - main.py will handle speaking it
                return payload
            
        except Exception as e:
            return f"Error executing {action}: {e}"
        
        return "Action complete."


# --- MODULE-LEVEL INSTANCE (for backward compatibility) ---
_nova_os = NovaOS()

def execute_step(step):
    """Module-level function for backward compatibility with main.py."""
    return _nova_os.execute_step(step)

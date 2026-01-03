import os
import time
import shutil
import pyautogui
import psutil
import datetime
import pygetwindow as gw

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
ADDITIONAL_SITES = {
    # --- Productivity & Tools ---
    "zoom": "zoom.us",
    "slack": "slack.com",
    "trello": "trello.com",
    "notion": "notion.so",
    "asana": "asana.com",
    "canva": "canva.com",
    "figma": "figma.com",
    "dropbox": "dropbox.com",
    "wetransfer": "wetransfer.com",
    "evernote": "evernote.com",
    "miro": "miro.com",
    "clickup": "clickup.com",
    "jira": "atlassian.com/software/jira",
    "office": "office.com",
    "outlook": "outlook.live.com",
    "onedrive": "onedrive.live.com",
    "teams": "teams.microsoft.com",
    "speedtest": "speedtest.net",
    "translate": "translate.google.com",
    "grammarly": "grammarly.com",
    "quillbot": "quillbot.com",
    "calendar": "calendar.google.com",
    "photos": "photos.google.com",
    "drive": "drive.google.com",
    "docs": "docs.google.com",
    "sheets": "docs.google.com/spreadsheets",
    "slides": "docs.google.com/presentation",

    # --- Development & Tech ---
    "gitlab": "gitlab.com",
    "bitbucket": "bitbucket.org",
    "leetcode": "leetcode.com",
    "hackerrank": "hackerrank.com",
    "geeksforgeeks": "geeksforgeeks.org",
    "w3schools": "w3schools.com",
    "kaggle": "kaggle.com",
    "huggingface": "huggingface.co",
    "replit": "replit.com",
    "codepen": "codepen.io",
    "vercel": "vercel.com",
    "netlify": "netlify.com",
    "digitalocean": "digitalocean.com",
    "aws": "aws.amazon.com",
    "azure": "azure.microsoft.com",
    "docker": "hub.docker.com",
    "pypi": "pypi.org",
    "npm": "npmjs.com",
    "devto": "dev.to",
    "medium": "medium.com",

    # --- News & Information ---
    "bbc": "bbc.com",
    "cnn": "cnn.com",
    "nytimes": "nytimes.com",
    "theguardian": "theguardian.com",
    "forbes": "forbes.com",
    "bloomberg": "bloomberg.com",
    "businessinsider": "businessinsider.com",
    "techcrunch": "techcrunch.com",
    "theverge": "theverge.com",
    "wired": "wired.com",
    "engadget": "engadget.com",
    "cnet": "cnet.com",
    "gsmarena": "gsmarena.com",
    "dawn": "dawn.com",  # Popular in PK
    "geo": "geo.tv",    # Popular in PK
    "weather": "weather.com",
    "wolframalpha": "wolframalpha.com",

    # --- Entertainment & Streaming ---
    "hulu": "hulu.com",
    "disneyplus": "disneyplus.com",
    "hbo": "max.com",
    "vimeo": "vimeo.com",
    "dailymotion": "dailymotion.com",
    "soundcloud": "soundcloud.com",
    "bandcamp": "bandcamp.com",
    "imdb": "imdb.com",
    "rottentomatoes": "rottentomatoes.com",
    "9gag": "9gag.com",
    "buzzfeed": "buzzfeed.com",

    # --- Education ---
    "coursera": "coursera.org",
    "udemy": "udemy.com",
    "edx": "edx.org",
    "khanacademy": "khanacademy.org",
    "quizlet": "quizlet.com",
    "duolingo": "duolingo.com",
    "chegg": "chegg.com",
    "scribd": "scribd.com",
    "researchgate": "researchgate.net",
    "academia": "academia.edu",

    # --- Shopping & E-Commerce ---
    "ebay": "ebay.com",
    "aliexpress": "aliexpress.com",
    "alibaba": "alibaba.com",
    "daraz": "daraz.pk", # Popular in PK
    "etsy": "etsy.com",
    "walmart": "walmart.com",
    "bestbuy": "bestbuy.com",
    "ikea": "ikea.com",
    "shopify": "shopify.com",

    # --- Finance & Crypto ---
    "paypal": "paypal.com",
    "binance": "binance.com",
    "coinbase": "coinbase.com",
    "tradingview": "tradingview.com",
    "wise": "wise.com",
    "payoneer": "payoneer.com",
    "stripe": "stripe.com",

    # --- Social & Messaging ---
    "telegram": "web.telegram.org",
    "snapchat": "snapchat.com",
    "tumblr": "tumblr.com",
    "quora": "quora.com",
    "wechat": "wechat.com",
    "skype": "web.skype.com",
    "messenger": "messenger.com",

    # --- Travel & Lifestyle ---
    "airbnb": "airbnb.com",
    "booking": "booking.com",
    "tripadvisor": "tripadvisor.com",
    "uber": "uber.com",
    "foodpanda": "foodpanda.pk", # Popular in PK

    # --- AI ---
    "claude": "claude.ai",
    "gemini": "gemini.google.com",
    "midjourney": "midjourney.com",
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

    except Exception as e:
        return f"Error executing {action}: {e}"
        
    return "Action complete."

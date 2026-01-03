"""
Nova Brain - The Agent Loop
LLM-powered intent recognition and action dispatch.
LIGHTNING MODE: Local fast-path for common commands.
"""

import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

# Load environment variables from .env file
load_dotenv()

# Load API key from environment variable
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set. See .env.example")


# =============================================================================
# LIGHTNING FAST-PATH: Local command parser (NO LLM, instant)
# =============================================================================

QUICK_SITES = {
    "youtube": "youtube", "google": "google", "facebook": "facebook",
    "twitter": "twitter", "x": "twitter", "instagram": "instagram",
    "reddit": "reddit", "github": "github", "linkedin": "linkedin",
    "amazon": "amazon", "netflix": "netflix", "spotify": "spotify",
    "twitch": "twitch", "discord": "discord", "chatgpt": "chatgpt",
    "gmail": "gmail", "wikipedia": "wikipedia",
}

QUICK_APPS = {
    "notepad": "notepad", "calculator": "calc", "calc": "calc",
    "explorer": "explorer", "file explorer": "explorer", "files": "explorer",
    "settings": "ms-settings:", "chrome": "chrome", "brave": "brave",
    "word": "winword", "excel": "excel", "vscode": "code", "vs code": "code",
    "terminal": "wt", "cmd": "cmd", "task manager": "taskmgr",
}

def fast_parse(user_text):
    """INSTANT command parser - bypasses LLM."""
    text = user_text.lower().strip()
    
    if text in ["hello", "hi", "hey"]:
        return {"plan": [{"action": "RESPONSE", "payload": "Ready."}]}
    if "thank" in text:
        return {"plan": [{"action": "RESPONSE", "payload": "Copy that."}]}
    
    # "Open [target]"
    open_match = re.match(r'^(?:open|go to|launch|start|visit)\s+(.+)$', text)
    if open_match:
        target = open_match.group(1).strip()
        for site_name, site_key in QUICK_SITES.items():
            if site_name in target:
                return {"plan": [{"action": "BROWSER", "payload": site_key}, {"action": "RESPONSE", "payload": f"Opening {site_key}."}]}
        for app_name, app_cmd in QUICK_APPS.items():
            if app_name in target:
                return {"plan": [{"action": "LAUNCH_SYS", "payload": app_cmd}, {"action": "RESPONSE", "payload": "Launching."}]}
    
    # "Play [song]"
    play_match = re.match(r'^play\s+(.+?)(?:\s+on\s+youtube)?$', text)
    if play_match:
        song = play_match.group(1).strip()
        if len(song) > 2:
            return {"plan": [{"action": "PLAY_MUSIC", "payload": song}, {"action": "RESPONSE", "payload": f"Playing {song}."}]}
    
    if any(p in text for p in ["minimize all", "show desktop"]):
        return {"plan": [{"action": "MINIMIZE_ALL", "payload": ""}, {"action": "RESPONSE", "payload": "Done."}]}
    
    if "screenshot" in text:
        return {"plan": [{"action": "SCREENSHOT", "payload": "capture"}, {"action": "RESPONSE", "payload": "Captured."}]}
    
    return None

# --- SYSTEM PROMPT: THE OPERATOR ---
sys_msg = """
You are NOVA, a precise Desktop Operator.
You do not guess. You do not chat. You execute.

Your goal is to translate user requests into a JSON PLAN of actions.
If the user asks for something complex, break it down.

AVAILABLE TOOLS:
1. "LAUNCH_SYS": For native apps.
   - Payloads: "calc", "notepad", "explorer", "ms-settings:"
   - Use this for "Open" commands (e.g., "Open Desktop").
2. "FILE_OPS": For creating, deleting, or moving files/folders.
   - Payload: {"operation": "CREATE" | "DELETE", "path": "..."}
   - PATH RULE: Resolve 'Desktop', 'Downloads', 'Documents' to "%USERPROFILE%\\Desktop", etc.
3. "BROWSER": For opening any website.
   - Payload: Site Name ONLY (e.g., "OLX", "GitHub", "Pinterest", "Reddit").
   - The action engine has a "Direct Knowledge" dictionary. It knows common sites (OLX, YouTube, Facebook, WhatsApp, ChatGPT, etc.) and will navigate directly.
   - For unknown sites, it will Google them and click the first result automatically.
   - RULE: Do NOT guess URLs or '.com' extensions. Just send the site name.
   - If user wants to go to a website, use BROWSER.
4. "PLAY_MUSIC": SPECIFICALLY for playing music via YouTube.
   - Payload: The EXACT song title ONLY (e.g., "Starboy", "Blinding Lights").
   - Uses Brave Browser and YouTube to play the requested song.
   - STRICT BAN: NEVER output a URL for the PLAY_MUSIC action.
   - CLEANING RULE: Remove "play", "on youtube", "on spotify" from the payload. Just the song name.
   - VALIDATION RULE: If the song name is unclear or less than 2 characters, output RESPONSE: "Could you repeat the song name?" instead of guessing.
   - FULL NAME RULE: You MUST capture the FULL song name. Do NOT truncate or shorten it.
   - If the user mentions 'Play [Song]' or any music request, the action MUST be PLAY_MUSIC.
5. "TYPE_STRING": To type text or equations into the active window.
   - Payload: The exact string to type.
   - VERBATIM RULE: The payload must be the EXACT text the user dictated, word-for-word. Do not summarize.
   - MATH RULE: If the user asks for a calculation (e.g., "calculate 2+2"), output the full equation as TYPE_STRING ("2+2"), followed by a PRESS_KEY ("enter").
6. "PRESS_KEY": To press keys.
   - Payloads: 'enter', 'win', 'ctrl+c', etc.
7. "SYSTEM_CHECK": For hardware status reports.
   - Payload: "" (Empty string).
   - Triggers: "Status report", "System health", "How is the CPU?", "Check CPU", "Battery status", "Memory usage".
8. "PROTOCOL": For complex multi-app macros.
   - Payload: "CODING" | "SOCIAL" | "GAMING".
   - Triggers: "Initiate Coding Mode", "Social Protocol", "Gaming Mode".
9. "SCREENSHOT": To capture the screen.
   - Payload: A filename or description (e.g., "evidence").
   - Triggers: "Take a screenshot", "Capture this".
10. "DOWNLOAD_WEB": For downloading and installing software via browser.
   - Payload: The name of the app (e.g., "VLC", "Chrome", "Steam", "Discord").
   - Triggers: "Download [App]", "Install [App]", "Get [App]".
   - RULE: Do NOT use command line tools. This opens the browser and clicks download.
11. "RESPONSE": To speak to the user.
   - TRUTH RULE: Only say "Opened [Site]" after the new tab is active and loading.

EXAMPLE 1: "Create a folder named ProjectX on my Desktop"
JSON:
{
  "plan": [
    {"action": "FILE_OPS", "payload": {"operation": "CREATE", "path": "%USERPROFILE%\\\\Desktop\\\\ProjectX"}},
    {"action": "RESPONSE", "payload": "Created folder ProjectX on Desktop."}
  ]
}

EXAMPLE 2: "Open Notepad and write a poem about code"
JSON:
{
  "plan": [
    {"action": "LAUNCH_SYS", "payload": "notepad"},
    {"action": "TYPE_STRING", "payload": "Code is poetry in motion,\\nA digital ocean..."},
    {"action": "RESPONSE", "payload": "Typed poem in Notepad."}
  ]
}

EXAMPLE 3: "Status report"
JSON:
{
  "plan": [
    {"action": "SYSTEM_CHECK", "payload": ""},
    {"action": "RESPONSE", "payload": "Systems check complete."}
  ]
}

EXAMPLE 4: "Initiate Coding Mode"
JSON:
{
  "plan": [
    {"action": "PROTOCOL", "payload": "CODING"},
    {"action": "RESPONSE", "payload": "Coding Protocol Initiated."}
  ]
}

EXAMPLE 5: "Download VLC"
JSON:
{
  "plan": [
    {"action": "DOWNLOAD_WEB", "payload": "VLC"},
    {"action": "RESPONSE", "payload": "Navigated to download page and triggered download."}
  ]
}
"""


class NovaAgent:
    """
    The thinking layer of Nova (OOP version).
    Uses LLM to parse commands and can dispatch to NovaOS.
    """
    
    def __init__(self):
        """Initialize the agent with LLM client."""
        self.client = Groq(api_key=API_KEY)
        # Lazy import to avoid circular dependency
        try:
            from nova_os import NovaOS
            self.os = NovaOS()
        except ImportError:
            self.os = None
        print("🧠 NovaAgent initialized.")
    
    def think(self, user_input):
        """Use LLM to parse user input into action plan."""
        try:
            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": sys_msg},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.0,
                response_format={"type": "json_object"}
            )
            result = json.loads(completion.choices[0].message.content)
            return result.get("plan", [])
        except Exception as e:
            print(f"❌ Think Error: {e}")
            return [{"action": "RESPONSE", "payload": "I encountered an error."}]
    
    def process_command(self, user_input):
        """Full pipeline: Input -> Think -> Return Plan."""
        print(f"\n💬 INPUT: '{user_input}'")
        plan = self.think(user_input)
        print(f"📋 PLAN: {plan}")
        return {"plan": plan}


# --- LEGACY FUNCTION (for backward compatibility with main.py) ---
client = Groq(api_key=API_KEY)

def get_operator_plan(user_text):
    """LIGHTNING-FAST: Try local parser first, LLM only for complex."""
    # FAST PATH (~0ms)
    fast_result = fast_parse(user_text)
    if fast_result:
        print(f"[FAST] {user_text}")
        return fast_result
    
    # SLOW PATH - LLM
    print(f"[LLM] {user_text}")
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": user_text}
            ],
            temperature=0.0,
            response_format={"type": "json_object"}
        )
        return json.loads(completion.choices[0].message.content)
    except Exception as e:
        print(f"Brain Error: {e}")
        return {"plan": [{"action": "RESPONSE", "payload": "Error."}]}
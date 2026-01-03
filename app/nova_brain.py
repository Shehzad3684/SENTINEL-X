"""
███╗   ██╗ ██████╗ ██╗   ██╗ █████╗     ██████╗ ██████╗  █████╗ ██╗███╗   ██╗
████╗  ██║██╔═══██╗██║   ██║██╔══██╗    ██╔══██╗██╔══██╗██╔══██╗██║████╗  ██║
██╔██╗ ██║██║   ██║██║   ██║███████║    ██████╔╝██████╔╝███████║██║██╔██╗ ██║
██║╚██╗██║██║   ██║╚██╗ ██╔╝██╔══██║    ██╔══██╗██╔══██╗██╔══██║██║██║╚██╗██║
██║ ╚████║╚██████╔╝ ╚████╔╝ ██║  ██║    ██████╔╝██║  ██║██║  ██║██║██║ ╚████║
╚═╝  ╚═══╝ ╚═════╝   ╚═══╝  ╚═╝  ╚═╝    ╚═════╝ ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝

NOVA BRAIN v3.0 - Intelligent Command Processing
Integrated with Sentinel Core for safe, accurate execution.
"""

import json
import os
import re
from dotenv import load_dotenv
from groq import Groq

# Import Sentinel Core
from app.sentinel_core import (
    get_sentinel, 
    Intent, 
    DOMAIN_MAP, 
    Personality
)

# Load environment variables
load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY environment variable not set. See .env.example")


# =============================================================================
# SYSTEM PROMPT - JARVIS Personality
# =============================================================================

SYSTEM_PROMPT = """You are SENTINEL-X, a calm, precise AI assistant. Think JARVIS from Iron Man.

PERSONALITY:
- Calm, professional, slightly witty
- Never verbose - MAX 15 words per response
- Never cringe or overly friendly
- When uncertain, ask ONE clear question

STRICT RULES:
1. NEVER open browsers for greetings like "hello", "hi", "hey"
2. NEVER guess websites - only use EXACT domains you know
3. NEVER repeat actions - if something was just done, acknowledge it
4. For questions: Use CHAT action, NO other actions
5. For actions: Be precise, one action at a time

INTENT CLASSIFICATION (do this FIRST):
- Greeting/chat: "hello", "hi", "how are you" → CHAT only, NO actions
- Questions: "what", "how", "why", "can you" → CHAT only, NO actions  
- Website: "open youtube", "go to google" → BROWSER_DIRECT
- App: "open notepad", "launch chrome" → LAUNCH_SYS
- Music: "play [song]" → PLAY_MUSIC
- System: "screenshot", "lock pc" → WINDOWS_SHORTCUT

AVAILABLE ACTIONS:
1. CHAT - For conversations. Payload: your response (MAX 15 words)
2. RESPONSE - For acknowledgments. Payload: short confirmation
3. BROWSER_DIRECT - Open URL directly. Payload: FULL URL (https://...)
4. LAUNCH_SYS - Open app. Payload: app name
5. PLAY_MUSIC - Play on YouTube. Payload: song name only
6. WINDOWS_SHORTCUT - System shortcuts. Payload: command description
7. TYPE_STRING - Type text. Payload: exact text
8. SCREENSHOT - Capture screen. Payload: "capture"

CRITICAL - What NOT to do:
- "hello" → DO NOT open any browser. Just respond with CHAT.
- "hi" → DO NOT open any browser. Just respond.
- Unknown site → DO NOT guess. Ask for clarification.
- Repeated request → DO NOT execute again. Say "Already done."

RESPONSE FORMAT (JSON only):
{
  "plan": [
    {"action": "ACTION_NAME", "payload": "value"}
  ]
}

EXAMPLES:

User: "hello"
{"plan": [{"action": "CHAT", "payload": "Ready when you are."}]}

User: "hi there"
{"plan": [{"action": "CHAT", "payload": "Standing by."}]}

User: "what can you do"
{"plan": [{"action": "CHAT", "payload": "Open apps, browse web, play music, screenshots, system control."}]}

User: "open youtube"
{"plan": [{"action": "BROWSER_DIRECT", "payload": "https://www.youtube.com"}, {"action": "RESPONSE", "payload": "Opening YouTube."}]}

User: "open olx"
{"plan": [{"action": "BROWSER_DIRECT", "payload": "https://www.olx.com.pk"}, {"action": "RESPONSE", "payload": "Opening OLX."}]}

User: "open daraz"
{"plan": [{"action": "BROWSER_DIRECT", "payload": "https://www.daraz.pk"}, {"action": "RESPONSE", "payload": "Opening Daraz."}]}

User: "play starboy"
{"plan": [{"action": "PLAY_MUSIC", "payload": "starboy"}, {"action": "RESPONSE", "payload": "Playing Starboy."}]}

User: "open notepad"
{"plan": [{"action": "LAUNCH_SYS", "payload": "notepad"}, {"action": "RESPONSE", "payload": "Launching Notepad."}]}

User: "take a screenshot"  
{"plan": [{"action": "SCREENSHOT", "payload": "capture"}, {"action": "RESPONSE", "payload": "Screenshot taken."}]}

User: "open somerandomsite"
{"plan": [{"action": "CHAT", "payload": "Don't recognize that site. What's the exact URL?"}]}
"""


# =============================================================================
# LOCAL FAST-PATH PROCESSOR
# =============================================================================

class FastPath:
    """
    Lightning-fast local processing for common commands.
    Bypasses LLM for instant response (~0ms).
    """
    
    # Conversational - NEVER trigger actions
    GREETINGS = {
        'hello', 'hi', 'hey', 'yo', 'sup', 'howdy', 'greetings',
        'good morning', 'good afternoon', 'good evening', 'good night',
        'whats up', "what's up", 'wassup'
    }
    
    THANKS = {'thanks', 'thank you', 'thx', 'ty', 'cheers'}
    
    GOODBYES = {'bye', 'goodbye', 'see ya', 'later', 'cya', 'peace'}
    
    AFFIRMATIVES = {'ok', 'okay', 'alright', 'sure', 'cool', 'nice', 'great', 'awesome', 'yes', 'yep', 'yeah'}
    
    # Stop commands
    STOPS = {'stop', 'cancel', 'abort', 'halt', 'nevermind', 'never mind', 'quit'}
    
    @classmethod
    def process(cls, text: str) -> dict:
        """
        Fast local processing. Returns plan or None if LLM needed.
        """
        text_clean = text.lower().strip()
        text_words = set(text_clean.replace("'", "").split())
        
        # 1. STOP COMMANDS - Highest priority
        if text_clean in cls.STOPS or text_words & cls.STOPS:
            return {
                "plan": [{"action": "RESPONSE", "payload": "Stopped. All clear."}],
                "fast_path": True,
                "intent": "stop"
            }
        
        # 2. GREETINGS - NO ACTIONS
        if text_clean in cls.GREETINGS or any(g in text_clean for g in ['hello', 'hi ', 'hey ']):
            return {
                "plan": [{"action": "CHAT", "payload": Personality.get("greeting")}],
                "fast_path": True,
                "intent": "greeting"
            }
        
        # 3. THANKS - NO ACTIONS
        if text_clean in cls.THANKS or text_words & cls.THANKS:
            return {
                "plan": [{"action": "CHAT", "payload": Personality.get("thanks")}],
                "fast_path": True,
                "intent": "thanks"
            }
        
        # 4. GOODBYES - NO ACTIONS
        if text_clean in cls.GOODBYES or text_words & cls.GOODBYES:
            return {
                "plan": [{"action": "CHAT", "payload": Personality.get("goodbye")}],
                "fast_path": True,
                "intent": "goodbye"
            }
        
        # 5. Simple affirmatives - NO ACTIONS
        if text_clean in cls.AFFIRMATIVES:
            return {
                "plan": [{"action": "CHAT", "payload": "What do you need?"}],
                "fast_path": True,
                "intent": "affirmative"
            }
        
        # 6. Questions about the bot
        if text_clean in ['who are you', 'what are you', "who're you"]:
            return {
                "plan": [{"action": "CHAT", "payload": "SENTINEL-X. Your AI assistant."}],
                "fast_path": True,
                "intent": "identity"
            }
        
        if 'what can you do' in text_clean or 'your capabilities' in text_clean:
            return {
                "plan": [{"action": "CHAT", "payload": Personality.get("capabilities")}],
                "fast_path": True,
                "intent": "capabilities"
            }
        
        if text_clean in ['how are you', "how're you", 'how are you doing']:
            return {
                "plan": [{"action": "CHAT", "payload": "Operational. What do you need?"}],
                "fast_path": True,
                "intent": "status_question"
            }
        
        # 7. Website opening - Use Sentinel domain map
        open_match = re.match(r'^(?:open|go\s*to|visit|launch)\s+(.+?)(?:\s*\.\s*com|\s*\.\s*pk)?$', text_clean)
        if open_match:
            target = open_match.group(1).strip()
            target = re.sub(r'\s*(website|site|page)$', '', target).strip()
            
            # Check known domains
            if target in DOMAIN_MAP:
                url = DOMAIN_MAP[target]
                return {
                    "plan": [
                        {"action": "BROWSER_DIRECT", "payload": url},
                        {"action": "RESPONSE", "payload": f"Opening {target}."}
                    ],
                    "fast_path": True,
                    "intent": "open_website",
                    "target": target
                }
            
            # Check if it's an app
            apps = {
                'notepad': 'notepad', 'calculator': 'calc', 'calc': 'calc',
                'explorer': 'explorer', 'file explorer': 'explorer', 'files': 'explorer',
                'settings': 'ms-settings:', 'chrome': 'chrome', 'brave': 'brave',
                'firefox': 'firefox', 'edge': 'msedge', 'word': 'winword',
                'excel': 'excel', 'powerpoint': 'powerpnt', 'vscode': 'code',
                'vs code': 'code', 'terminal': 'wt', 'cmd': 'cmd',
                'task manager': 'taskmgr', 'paint': 'mspaint', 'whatsapp': 'whatsapp',
                'discord': 'discord', 'spotify': 'spotify', 'slack': 'slack'
            }
            
            if target in apps:
                return {
                    "plan": [
                        {"action": "LAUNCH_SYS", "payload": apps[target]},
                        {"action": "RESPONSE", "payload": f"Launching {target}."}
                    ],
                    "fast_path": True,
                    "intent": "open_app",
                    "target": target
                }
            
            # Unknown - don't guess, ask
            return {
                "plan": [{"action": "CHAT", "payload": f"Don't recognize '{target}'. What's the exact URL?"}],
                "fast_path": True,
                "intent": "unknown_site"
            }
        
        # 8. Play music
        play_match = re.match(r'^play\s+(.+?)(?:\s+on\s+youtube|\s+on\s+spotify|\s+music)?$', text_clean)
        if play_match:
            song = play_match.group(1).strip()
            if len(song) >= 2:
                return {
                    "plan": [
                        {"action": "PLAY_MUSIC", "payload": song},
                        {"action": "RESPONSE", "payload": f"Playing {song}."}
                    ],
                    "fast_path": True,
                    "intent": "play_music",
                    "target": song
                }
        
        # 9. Screenshot
        if any(kw in text_clean for kw in ['screenshot', 'screen shot', 'capture screen', 'take a picture']):
            return {
                "plan": [
                    {"action": "SCREENSHOT", "payload": "capture"},
                    {"action": "RESPONSE", "payload": "Screenshot taken."}
                ],
                "fast_path": True,
                "intent": "screenshot"
            }
        
        # 10. Minimize/Desktop
        if any(kw in text_clean for kw in ['minimize all', 'show desktop', 'clear screen', 'go to desktop']):
            return {
                "plan": [
                    {"action": "MINIMIZE_ALL", "payload": ""},
                    {"action": "RESPONSE", "payload": "Done."}
                ],
                "fast_path": True,
                "intent": "minimize"
            }
        
        # 11. Lock PC
        if any(kw in text_clean for kw in ['lock pc', 'lock computer', 'lock my pc', 'lock screen']):
            return {
                "plan": [
                    {"action": "WINDOWS_SHORTCUT", "payload": "lock pc"},
                    {"action": "RESPONSE", "payload": "Locking."}
                ],
                "fast_path": True,
                "intent": "lock"
            }
        
        # 12. System status
        if any(kw in text_clean for kw in ['status', 'system status', 'cpu', 'battery', 'memory usage']):
            return {
                "plan": [{"action": "SYSTEM_CHECK", "payload": ""}],
                "fast_path": True,
                "intent": "system_check"
            }
        
        # Not matched - need LLM
        return None


# =============================================================================
# LLM PROCESSOR  
# =============================================================================

class LLMProcessor:
    """
    Groq LLM for complex commands that can't be handled locally.
    """
    
    def __init__(self):
        self.client = Groq(api_key=API_KEY)
        self.model = "llama-3.1-8b-instant"
    
    def process(self, user_text: str) -> dict:
        """Process through LLM"""
        try:
            completion = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_text}
                ],
                temperature=0.0,  # Deterministic
                response_format={"type": "json_object"}
            )
            
            result = json.loads(completion.choices[0].message.content)
            result["fast_path"] = False
            result["intent"] = "llm_processed"
            
            # SAFETY: Validate the plan doesn't contain browser actions for greetings
            if self._is_conversational(user_text):
                # Filter out any non-CHAT/RESPONSE actions
                result["plan"] = [
                    action for action in result.get("plan", [])
                    if action.get("action") in ["CHAT", "RESPONSE"]
                ]
                
                # If empty, add default response
                if not result["plan"]:
                    result["plan"] = [{"action": "CHAT", "payload": "What do you need?"}]
            
            return result
            
        except Exception as e:
            print(f"[LLM ERROR] {e}")
            return {
                "plan": [{"action": "CHAT", "payload": "Had an issue processing that. Try again?"}],
                "fast_path": False,
                "intent": "error"
            }
    
    def _is_conversational(self, text: str) -> bool:
        """Check if input is conversational (should NOT trigger actions)"""
        text_lower = text.lower().strip()
        
        # Direct matches
        conversational = ['hello', 'hi', 'hey', 'yo', 'sup', 'thanks', 'thank you',
                         'bye', 'goodbye', 'ok', 'okay', 'yes', 'no', 'sure']
        
        if text_lower in conversational:
            return True
        
        # Question patterns
        if re.match(r'^(what|how|why|when|where|who|can|could|would|should|is|are|do|does)\b', text_lower):
            return True
        
        return False


# =============================================================================
# MAIN INTERFACE
# =============================================================================

# Global instances
_sentinel = None
_llm = None

def _get_sentinel():
    global _sentinel
    if _sentinel is None:
        _sentinel = get_sentinel()
    return _sentinel

def _get_llm():
    global _llm
    if _llm is None:
        _llm = LLMProcessor()
    return _llm


def get_operator_plan(user_text: str) -> dict:
    """
    MAIN ENTRY POINT - Process user command.
    
    Pipeline:
    1. Sentinel Core pre-check (safety, duplicates)
    2. Fast Path (local, ~0ms)
    3. LLM Fallback (complex commands)
    4. Post-validation
    """
    sentinel = _get_sentinel()
    
    # 1. Pre-check with Sentinel
    sentinel_result = sentinel.process(user_text)
    
    # If Sentinel blocked it (duplicate, already open, etc.)
    if sentinel_result.get("blocked"):
        print(f"[SENTINEL] Blocked: {sentinel_result.get('reason')}")
        return {
            "plan": [{"action": "RESPONSE", "payload": sentinel_result.get("response", "Blocked.")}]
        }
    
    # If Sentinel has a complete plan (conversational, known actions)
    if sentinel_result.get("plan") and sentinel_result["intent"] != Intent.UNKNOWN:
        # Check if it's a CHAT action that needs LLM
        if (len(sentinel_result["plan"]) == 1 and 
            sentinel_result["plan"][0].get("action") == "CHAT" and
            sentinel_result["plan"][0].get("payload") == user_text):
            # Needs LLM for actual response
            pass
        else:
            print(f"[SENTINEL] Handled: {sentinel_result['intent']}")
            return {"plan": sentinel_result["plan"]}
    
    # 2. Try Fast Path
    fast_result = FastPath.process(user_text)
    if fast_result:
        print(f"[FAST] {fast_result.get('intent', 'matched')}: {user_text}")
        return {"plan": fast_result["plan"]}
    
    # 3. LLM Fallback
    print(f"[LLM] Processing: {user_text}")
    llm = _get_llm()
    llm_result = llm.process(user_text)
    
    # 4. Post-validation - Ensure no browser actions for conversational input
    if llm._is_conversational(user_text):
        safe_plan = []
        for action in llm_result.get("plan", []):
            if action.get("action") in ["CHAT", "RESPONSE"]:
                safe_plan.append(action)
        
        if not safe_plan:
            safe_plan = [{"action": "CHAT", "payload": "What can I help with?"}]
        
        llm_result["plan"] = safe_plan
    
    return {"plan": llm_result.get("plan", [])}


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Keep old function signature for backward compatibility
def fast_parse(user_text: str) -> dict:
    """Legacy fast_parse - now uses FastPath class"""
    result = FastPath.process(user_text)
    return result if result else None

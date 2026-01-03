"""
███████╗███████╗███╗   ██╗████████╗██╗███╗   ██╗███████╗██╗     
██╔════╝██╔════╝████╗  ██║╚══██╔══╝██║████╗  ██║██╔════╝██║     
███████╗█████╗  ██╔██╗ ██║   ██║   ██║██╔██╗ ██║█████╗  ██║     
╚════██║██╔══╝  ██║╚██╗██║   ██║   ██║██║╚██╗██║██╔══╝  ██║     
███████║███████╗██║ ╚████║   ██║   ██║██║ ╚████║███████╗███████╗
╚══════╝╚══════╝╚═╝  ╚═══╝   ╚═╝   ╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝

SENTINEL CORE - Intelligent Action Safety Layer
Prevents infinite loops, enforces intent classification, ensures deterministic behavior.
"""

import time
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple
from enum import Enum, auto
from collections import deque


# =============================================================================
# INTENT CLASSIFICATION SYSTEM
# =============================================================================

class Intent(Enum):
    """All possible user intents - mutually exclusive"""
    CONVERSATIONAL = auto()      # Greeting, chat, questions
    OPEN_WEBSITE = auto()        # Open specific website
    OPEN_APP = auto()            # Open local application
    SEARCH_QUERY = auto()        # Search for something online
    PLAY_MEDIA = auto()          # Play music/video
    BROWSER_CONTROL = auto()     # Tab management, refresh, etc.
    SYSTEM_CONTROL = auto()      # Shutdown, restart, lock, etc.
    FILE_OPERATION = auto()      # Create, delete, move files
    TYPE_TEXT = auto()           # Type something
    SCREENSHOT = auto()          # Capture screen
    MULTI_STEP = auto()          # Complex multi-step command
    STOP_COMMAND = auto()        # Abort/cancel/stop
    UNKNOWN = auto()             # Need clarification


# Conversational triggers - NEVER execute actions for these
CONVERSATIONAL_PATTERNS = [
    # Greetings (with optional words after)
    r'^(hi|hello|hey|yo|sup|howdy|greetings?)\b.*$',
    r'^good\s*(morning|afternoon|evening|night).*$',
    r'^what\'?s?\s*up.*$',
    r'^how\'?s?\s*it\s*going.*$',
    
    # Thanks/Bye
    r'^(thanks?|thank\s*you|thx|ty)\b.*$',
    r'^(bye|goodbye|see\s*ya|later|cya)\b.*$',
    r'^(ok|okay|alright|sure|cool|nice|great|awesome)[\s!.?]*$',
    
    # Questions about the bot
    r'^who\s*(are|r)\s*you',
    r'^what\s*(are|r)\s*you',
    r'^what\s*can\s*you\s*do',
    r'^(can|could|will|would)\s*you\s*(help|assist)',
    r'^tell\s*me\s*about\s*(yourself|you)',
    r'^how\s*(are|r)\s*you',
    r'^are\s*you\s*(there|alive|ready|listening)',
    
    # General questions (not action requests)
    r'^(what|how|why|when|where|who)\s+(is|are|was|were|do|does|did|can|could|would|should)\b',
    r'^(do|does|did|can|could|would|should|is|are)\s+(you|it|this|that)\b',
    r'^(explain|describe|tell\s*me)\b',
]

# Stop commands - immediate halt
STOP_PATTERNS = [
    r'^stop[\s!.]*$',
    r'^cancel[\s!.]*$',
    r'^abort[\s!.]*$',
    r'^halt[\s!.]*$',
    r'^nevermind[\s!.]*$',
    r'^never\s*mind[\s!.]*$',
    r'^quit[\s!.]*$',
    r'^exit[\s!.]*$',
]

# Website patterns
WEBSITE_PATTERNS = [
    r'(?:open|go\s*to|visit|launch|load|navigate\s*to)\s+(.+?)(?:\s+website|\s+site)?$',
]

# App patterns  
APP_PATTERNS = [
    r'(?:open|launch|start|run)\s+(notepad|calculator|calc|explorer|settings|word|excel|powerpoint|chrome|brave|firefox|vscode|code|terminal|cmd|powershell)(?:\s+app)?',
]

# Play media patterns
PLAY_PATTERNS = [
    r'play\s+(.+?)(?:\s+on\s+youtube|\s+on\s+spotify|\s+music)?$',
]


# =============================================================================
# ABSOLUTE DOMAIN MAPPING - NO GUESSING
# =============================================================================

DOMAIN_MAP = {
    # Shopping
    "olx": "https://www.olx.com.pk",
    "daraz": "https://www.daraz.pk",
    "amazon": "https://www.amazon.com",
    "ebay": "https://www.ebay.com",
    "aliexpress": "https://www.aliexpress.com",
    
    # Social Media
    "facebook": "https://www.facebook.com",
    "twitter": "https://twitter.com",
    "x": "https://twitter.com",
    "instagram": "https://www.instagram.com",
    "linkedin": "https://www.linkedin.com",
    "reddit": "https://www.reddit.com",
    "pinterest": "https://www.pinterest.com",
    "tiktok": "https://www.tiktok.com",
    "snapchat": "https://www.snapchat.com",
    
    # Video/Streaming
    "youtube": "https://www.youtube.com",
    "netflix": "https://www.netflix.com",
    "twitch": "https://www.twitch.tv",
    "hulu": "https://www.hulu.com",
    "disney": "https://www.disneyplus.com",
    "prime video": "https://www.primevideo.com",
    
    # Productivity
    "google": "https://www.google.com",
    "gmail": "https://mail.google.com",
    "google drive": "https://drive.google.com",
    "google docs": "https://docs.google.com",
    "outlook": "https://outlook.live.com",
    "notion": "https://www.notion.so",
    "trello": "https://trello.com",
    
    # Dev/Tech
    "github": "https://github.com",
    "gitlab": "https://gitlab.com",
    "stackoverflow": "https://stackoverflow.com",
    "stack overflow": "https://stackoverflow.com",
    "chatgpt": "https://chat.openai.com",
    "chat gpt": "https://chat.openai.com",
    "openai": "https://www.openai.com",
    "claude": "https://claude.ai",
    
    # Communication
    "discord": "https://discord.com/app",
    "slack": "https://slack.com",
    "whatsapp": "https://web.whatsapp.com",
    "whatsapp web": "https://web.whatsapp.com",
    "telegram": "https://web.telegram.org",
    "zoom": "https://zoom.us",
    "teams": "https://teams.microsoft.com",
    
    # Music
    "spotify": "https://open.spotify.com",
    "soundcloud": "https://soundcloud.com",
    "apple music": "https://music.apple.com",
    
    # News/Info
    "wikipedia": "https://www.wikipedia.org",
    "bbc": "https://www.bbc.com",
    "cnn": "https://www.cnn.com",
    
    # Other
    "canva": "https://www.canva.com",
    "figma": "https://www.figma.com",
}


# =============================================================================
# ACTION EXECUTION GUARD
# =============================================================================

@dataclass
class ExecutedAction:
    """Record of an executed action"""
    action_type: str
    target: str
    timestamp: float
    
    def matches(self, other_type: str, other_target: str) -> bool:
        """Check if this action matches another"""
        return (self.action_type == other_type and 
                self.target.lower() == other_target.lower())


class ActionGuard:
    """
    Prevents infinite loops and duplicate actions.
    CRITICAL SAFETY LAYER - DO NOT BYPASS.
    """
    
    # Cooldown in seconds before same action can repeat
    ACTION_COOLDOWN = 5.0
    
    # Max times an action can repeat before hard block
    MAX_REPEATS = 2
    
    def __init__(self):
        self.history: deque = deque(maxlen=50)  # Last 50 actions
        self.repeat_counts: Dict[str, int] = {}
        self.blocked_until: float = 0
        self.last_action_time: float = 0
    
    def _action_key(self, action_type: str, target: str) -> str:
        """Generate unique key for action"""
        return f"{action_type}:{target.lower()}"
    
    def can_execute(self, action_type: str, target: str) -> Tuple[bool, str]:
        """
        Check if action can be executed.
        Returns (allowed, reason)
        """
        now = time.time()
        key = self._action_key(action_type, target)
        
        # Check if globally blocked
        if now < self.blocked_until:
            return False, "System paused due to repeated actions. Say 'continue' to resume."
        
        # Check recent history for duplicates
        for action in self.history:
            if action.matches(action_type, target):
                time_diff = now - action.timestamp
                
                if time_diff < self.ACTION_COOLDOWN:
                    # Increment repeat count
                    self.repeat_counts[key] = self.repeat_counts.get(key, 0) + 1
                    
                    if self.repeat_counts[key] >= self.MAX_REPEATS:
                        # Hard block
                        self.blocked_until = now + 30  # 30 second cooldown
                        return False, f"Blocked: '{target}' was requested {self.MAX_REPEATS}+ times. Pausing for safety."
                    
                    return False, f"Already done. {target} was just opened {time_diff:.1f}s ago."
        
        return True, "OK"
    
    def record(self, action_type: str, target: str):
        """Record an executed action"""
        now = time.time()
        self.history.append(ExecutedAction(action_type, target, now))
        self.last_action_time = now
        
        # Decay repeat counts over time
        key = self._action_key(action_type, target)
        if key in self.repeat_counts:
            self.repeat_counts[key] = max(0, self.repeat_counts[key] - 1)
    
    def clear(self):
        """Clear all history (for stop command)"""
        self.history.clear()
        self.repeat_counts.clear()
        self.blocked_until = 0
    
    def force_unblock(self):
        """Unblock after user confirmation"""
        self.blocked_until = 0
        self.repeat_counts.clear()


# =============================================================================
# SESSION CONTEXT
# =============================================================================

@dataclass
class SessionContext:
    """Tracks session state for context-aware responses"""
    
    open_websites: Set[str] = field(default_factory=set)
    open_apps: Set[str] = field(default_factory=set)
    last_command: str = ""
    last_action: str = ""
    last_target: str = ""
    conversation_count: int = 0
    
    def update(self, command: str, action: str, target: str):
        """Update context after command execution"""
        self.last_command = command
        self.last_action = action
        self.last_target = target
        
        if action == "BROWSER":
            self.open_websites.add(target.lower())
        elif action == "LAUNCH_SYS":
            self.open_apps.add(target.lower())
    
    def is_already_open(self, target: str, action_type: str) -> bool:
        """Check if target is already open"""
        target_lower = target.lower()
        if action_type == "BROWSER":
            return target_lower in self.open_websites
        elif action_type == "LAUNCH_SYS":
            return target_lower in self.open_apps
        return False
    
    def mark_closed(self, target: str, action_type: str):
        """Mark target as closed"""
        target_lower = target.lower()
        if action_type == "BROWSER":
            self.open_websites.discard(target_lower)
        elif action_type == "LAUNCH_SYS":
            self.open_apps.discard(target_lower)


# =============================================================================
# JARVIS PERSONALITY
# =============================================================================

class Personality:
    """JARVIS-like response generator - calm, witty, sharp"""
    
    # Acknowledgments - short and professional
    ACK_DONE = [
        "Done.",
        "That's handled.",
        "Taken care of.",
        "On it.",
        "Completed.",
    ]
    
    ACK_ALREADY = [
        "Already open.",
        "That's already running.",
        "Still there. Want me to refresh?",
        "Already done. I don't forget that fast.",
        "It's open. Need me to bring it forward?",
    ]
    
    ACK_BLOCKED = [
        "Hold on. You just asked for that.",
        "I heard you the first time.",
        "Still on cooldown. Give it a moment.",
        "That's a duplicate. Skipping.",
    ]
    
    GREETINGS = [
        "Ready when you are.",
        "Standing by.",
        "At your service.",
        "Online and listening.",
        "What do you need?",
    ]
    
    GOODBYES = [
        "Standing down.",
        "Going quiet.",
        "Call if you need me.",
        "Offline.",
    ]
    
    THANKS_RESPONSES = [
        "Anytime.",
        "That's what I'm here for.",
        "Copy that.",
        "No problem.",
    ]
    
    UNKNOWN_SITE = [
        "Don't recognize that site. Can you spell it out?",
        "Not in my records. What's the exact URL?",
        "Unknown domain. Full address please?",
    ]
    
    ERROR_RESPONSES = [
        "That didn't work. {reason}",
        "Hit a snag. {reason}",
        "Error: {reason}",
    ]
    
    CAPABILITIES = (
        "Open apps, websites, play music, type text, "
        "screenshots, system control. What do you need?"
    )
    
    @classmethod
    def get(cls, category: str, **kwargs) -> str:
        """Get a response from a category"""
        import random
        
        responses = {
            "done": cls.ACK_DONE,
            "already": cls.ACK_ALREADY,
            "blocked": cls.ACK_BLOCKED,
            "greeting": cls.GREETINGS,
            "goodbye": cls.GOODBYES,
            "thanks": cls.THANKS_RESPONSES,
            "unknown_site": cls.UNKNOWN_SITE,
            "error": cls.ERROR_RESPONSES,
            "capabilities": [cls.CAPABILITIES],
        }
        
        options = responses.get(category, ["Acknowledged."])
        response = random.choice(options)
        
        # Format with kwargs if needed
        if kwargs:
            response = response.format(**kwargs)
        
        return response


# =============================================================================
# INTENT CLASSIFIER
# =============================================================================

class IntentClassifier:
    """
    Classifies user input into specific intents.
    This is the PRIMARY decision maker - actions only happen if intent is clear.
    """
    
    @staticmethod
    def classify(text: str) -> Tuple[Intent, Optional[str]]:
        """
        Classify user input into an intent.
        Returns (Intent, extracted_target or None)
        """
        text_lower = text.lower().strip()
        
        # 1. STOP COMMANDS - Highest priority
        for pattern in STOP_PATTERNS:
            if re.match(pattern, text_lower):
                return Intent.STOP_COMMAND, None
        
        # 2. CONVERSATIONAL - Check before any action
        for pattern in CONVERSATIONAL_PATTERNS:
            if re.match(pattern, text_lower):
                return Intent.CONVERSATIONAL, text_lower
        
        # 3. Check for question words (not action requests)
        question_starters = ['what', 'how', 'why', 'when', 'where', 'who', 
                           'is it', 'are you', 'can you', 'do you', 'does it',
                           'would', 'could', 'should', 'will it', 'explain', 'tell me']
        
        for starter in question_starters:
            if text_lower.startswith(starter):
                # It's a question, not an action
                return Intent.CONVERSATIONAL, text_lower
        
        # 4. PLAY MEDIA
        for pattern in PLAY_PATTERNS:
            match = re.match(pattern, text_lower)
            if match:
                song = match.group(1).strip()
                return Intent.PLAY_MEDIA, song
        
        # 5. WEBSITE - Check domain map first
        # Pattern: "open X" where X is a known site
        open_match = re.match(r'(?:open|go\s*to|visit|launch)\s+(.+?)(?:\s*\.com|\s*\.pk|\s*\.org)?$', text_lower)
        if open_match:
            target = open_match.group(1).strip()
            
            # Remove common suffixes
            target = re.sub(r'\s*(website|site|page|app)$', '', target).strip()
            
            # Check if it's a known domain
            if target in DOMAIN_MAP:
                return Intent.OPEN_WEBSITE, target
            
            # Check if it's a known app
            app_names = ['notepad', 'calculator', 'calc', 'explorer', 'settings', 
                        'word', 'excel', 'powerpoint', 'chrome', 'brave', 
                        'firefox', 'vscode', 'code', 'terminal', 'cmd', 
                        'powershell', 'whatsapp', 'discord', 'spotify', 'slack',
                        'task manager', 'file explorer']
            
            if target in app_names:
                return Intent.OPEN_APP, target
            
            # Check for domain-like patterns (has .com, .org, etc.)
            if re.search(r'\.(com|org|net|pk|io|ai|dev|co)$', target):
                return Intent.OPEN_WEBSITE, target
            
            # Unknown target - might be website or app
            # Default to website but mark as potentially unknown
            return Intent.OPEN_WEBSITE, target
        
        # 6. SCREENSHOT
        if any(kw in text_lower for kw in ['screenshot', 'screen shot', 'capture', 'snap']):
            return Intent.SCREENSHOT, None
        
        # 7. SYSTEM CONTROL
        system_keywords = ['shutdown', 'restart', 'lock', 'sleep', 'hibernate',
                         'minimize', 'maximize', 'close', 'status', 'battery']
        if any(kw in text_lower for kw in system_keywords):
            return Intent.SYSTEM_CONTROL, text_lower
        
        # 8. BROWSER CONTROL
        browser_keywords = ['new tab', 'close tab', 'refresh', 'next tab', 'switch tab']
        if any(kw in text_lower for kw in browser_keywords):
            return Intent.BROWSER_CONTROL, text_lower
        
        # 9. TYPE TEXT
        if text_lower.startswith(('type ', 'write ', 'enter ')):
            content = re.sub(r'^(type|write|enter)\s+', '', text_lower)
            return Intent.TYPE_TEXT, content
        
        # 10. FILE OPERATION
        if any(kw in text_lower for kw in ['create folder', 'delete file', 'new folder', 'remove']):
            return Intent.FILE_OPERATION, text_lower
        
        # 11. MULTI-STEP (contains "and")
        if ' and ' in text_lower and any(kw in text_lower for kw in ['open', 'then', 'after']):
            return Intent.MULTI_STEP, text_lower
        
        # Default: Unknown - ask for clarification
        return Intent.UNKNOWN, text_lower


# =============================================================================
# SENTINEL CORE - Main Intelligence Layer
# =============================================================================

class SentinelCore:
    """
    The brain of SENTINEL-X.
    Coordinates intent classification, action safety, and response generation.
    """
    
    def __init__(self):
        self.guard = ActionGuard()
        self.context = SessionContext()
        self.classifier = IntentClassifier()
        
        print("[SENTINEL] Core initialized - Safety systems online")
    
    def process(self, user_input: str) -> dict:
        """
        Process user input and return action plan.
        This is the main entry point.
        
        Returns:
            {
                "intent": Intent enum,
                "plan": [...actions...],
                "response": "...",
                "blocked": bool,
                "reason": "..."
            }
        """
        user_input = user_input.strip()
        
        if not user_input:
            return {
                "intent": Intent.CONVERSATIONAL,
                "plan": [],
                "response": "I didn't catch that.",
                "blocked": False,
                "reason": ""
            }
        
        # Classify intent
        intent, target = self.classifier.classify(user_input)
        
        # Handle based on intent
        if intent == Intent.STOP_COMMAND:
            return self._handle_stop()
        
        if intent == Intent.CONVERSATIONAL:
            return self._handle_conversation(user_input, target)
        
        if intent == Intent.OPEN_WEBSITE:
            return self._handle_open_website(target)
        
        if intent == Intent.OPEN_APP:
            return self._handle_open_app(target)
        
        if intent == Intent.PLAY_MEDIA:
            return self._handle_play_media(target)
        
        if intent == Intent.SCREENSHOT:
            return self._handle_screenshot()
        
        if intent == Intent.SYSTEM_CONTROL:
            return self._handle_system_control(target)
        
        if intent == Intent.BROWSER_CONTROL:
            return self._handle_browser_control(target)
        
        if intent == Intent.TYPE_TEXT:
            return self._handle_type_text(target)
        
        if intent == Intent.UNKNOWN:
            return self._handle_unknown(user_input)
        
        # Fallback
        return {
            "intent": intent,
            "plan": [],
            "response": "I'm not sure what you want. Can you rephrase?",
            "blocked": False,
            "reason": "unknown_intent"
        }
    
    def _handle_stop(self) -> dict:
        """Handle stop/cancel command"""
        self.guard.clear()
        return {
            "intent": Intent.STOP_COMMAND,
            "plan": [],
            "response": "Stopped. All clear.",
            "blocked": False,
            "reason": ""
        }
    
    def _handle_conversation(self, user_input: str, target: str) -> dict:
        """Handle conversational input - NO ACTIONS"""
        self.context.conversation_count += 1
        
        text_lower = target or user_input.lower()
        
        # Determine response type
        if any(g in text_lower for g in ['hello', 'hi', 'hey', 'yo']):
            response = Personality.get("greeting")
        elif any(g in text_lower for g in ['bye', 'goodbye', 'see ya']):
            response = Personality.get("goodbye")
        elif any(g in text_lower for g in ['thank', 'thanks']):
            response = Personality.get("thanks")
        elif 'what can you do' in text_lower or 'capabilities' in text_lower:
            response = Personality.get("capabilities")
        elif 'who are you' in text_lower or 'what are you' in text_lower:
            response = "SENTINEL-X. Your AI assistant. Built for speed and precision."
        elif 'how are you' in text_lower:
            response = "Operational. Systems nominal."
        else:
            # Generic conversational response via CHAT
            return {
                "intent": Intent.CONVERSATIONAL,
                "plan": [{"action": "CHAT", "payload": user_input}],
                "response": None,  # Let LLM handle
                "blocked": False,
                "reason": ""
            }
        
        return {
            "intent": Intent.CONVERSATIONAL,
            "plan": [{"action": "RESPONSE", "payload": response}],
            "response": response,
            "blocked": False,
            "reason": ""
        }
    
    def _handle_open_website(self, target: str) -> dict:
        """Handle website opening with ABSOLUTE domain resolution"""
        
        # Normalize target
        target_clean = target.lower().strip()
        target_clean = re.sub(r'\s*(website|site|page)$', '', target_clean).strip()
        
        # Check domain map FIRST
        if target_clean in DOMAIN_MAP:
            url = DOMAIN_MAP[target_clean]
            
            # Safety check
            allowed, reason = self.guard.can_execute("BROWSER", target_clean)
            if not allowed:
                return {
                    "intent": Intent.OPEN_WEBSITE,
                    "plan": [],
                    "response": reason,
                    "blocked": True,
                    "reason": "duplicate_action"
                }
            
            # Check if already open
            if self.context.is_already_open(target_clean, "BROWSER"):
                return {
                    "intent": Intent.OPEN_WEBSITE,
                    "plan": [],
                    "response": Personality.get("already"),
                    "blocked": True,
                    "reason": "already_open"
                }
            
            # Execute
            self.guard.record("BROWSER", target_clean)
            self.context.update(f"open {target_clean}", "BROWSER", target_clean)
            
            return {
                "intent": Intent.OPEN_WEBSITE,
                "plan": [
                    {"action": "BROWSER_DIRECT", "payload": url},
                    {"action": "RESPONSE", "payload": f"Opening {target_clean}."}
                ],
                "response": f"Opening {target_clean}.",
                "blocked": False,
                "reason": ""
            }
        
        # Unknown domain - ASK, don't guess
        return {
            "intent": Intent.OPEN_WEBSITE,
            "plan": [],
            "response": Personality.get("unknown_site"),
            "blocked": True,
            "reason": "unknown_domain"
        }
    
    def _handle_open_app(self, target: str) -> dict:
        """Handle app launching"""
        
        # Safety check
        allowed, reason = self.guard.can_execute("LAUNCH_SYS", target)
        if not allowed:
            return {
                "intent": Intent.OPEN_APP,
                "plan": [],
                "response": reason,
                "blocked": True,
                "reason": "duplicate_action"
            }
        
        # Check if already open
        if self.context.is_already_open(target, "LAUNCH_SYS"):
            return {
                "intent": Intent.OPEN_APP,
                "plan": [],
                "response": Personality.get("already"),
                "blocked": True,
                "reason": "already_open"
            }
        
        # Execute
        self.guard.record("LAUNCH_SYS", target)
        self.context.update(f"open {target}", "LAUNCH_SYS", target)
        
        return {
            "intent": Intent.OPEN_APP,
            "plan": [
                {"action": "LAUNCH_SYS", "payload": target},
                {"action": "RESPONSE", "payload": f"Launching {target}."}
            ],
            "response": f"Launching {target}.",
            "blocked": False,
            "reason": ""
        }
    
    def _handle_play_media(self, song: str) -> dict:
        """Handle music playback"""
        
        if not song or len(song) < 2:
            return {
                "intent": Intent.PLAY_MEDIA,
                "plan": [],
                "response": "What should I play?",
                "blocked": True,
                "reason": "missing_song"
            }
        
        # Safety check
        allowed, reason = self.guard.can_execute("PLAY_MUSIC", song)
        if not allowed:
            return {
                "intent": Intent.PLAY_MEDIA,
                "plan": [],
                "response": reason,
                "blocked": True,
                "reason": "duplicate_action"
            }
        
        self.guard.record("PLAY_MUSIC", song)
        
        return {
            "intent": Intent.PLAY_MEDIA,
            "plan": [
                {"action": "PLAY_MUSIC", "payload": song},
                {"action": "RESPONSE", "payload": f"Playing {song}."}
            ],
            "response": f"Playing {song}.",
            "blocked": False,
            "reason": ""
        }
    
    def _handle_screenshot(self) -> dict:
        """Handle screenshot"""
        
        # Safety check (prevent spam)
        allowed, reason = self.guard.can_execute("SCREENSHOT", "screen")
        if not allowed:
            return {
                "intent": Intent.SCREENSHOT,
                "plan": [],
                "response": reason,
                "blocked": True,
                "reason": "duplicate_action"
            }
        
        self.guard.record("SCREENSHOT", "screen")
        
        return {
            "intent": Intent.SCREENSHOT,
            "plan": [
                {"action": "SCREENSHOT", "payload": "capture"},
                {"action": "RESPONSE", "payload": "Screenshot taken."}
            ],
            "response": "Screenshot taken.",
            "blocked": False,
            "reason": ""
        }
    
    def _handle_system_control(self, command: str) -> dict:
        """Handle system control commands with confirmation for risky ones"""
        
        risky_commands = ['shutdown', 'restart', 'delete', 'remove', 'format']
        
        if any(r in command for r in risky_commands):
            return {
                "intent": Intent.SYSTEM_CONTROL,
                "plan": [],
                "response": f"That's a risky action. Say 'confirm {command}' to proceed.",
                "blocked": True,
                "reason": "needs_confirmation"
            }
        
        # Safe system commands
        return {
            "intent": Intent.SYSTEM_CONTROL,
            "plan": [
                {"action": "WINDOWS_SHORTCUT", "payload": command},
                {"action": "RESPONSE", "payload": "Done."}
            ],
            "response": "Done.",
            "blocked": False,
            "reason": ""
        }
    
    def _handle_browser_control(self, command: str) -> dict:
        """Handle browser tab/window control"""
        return {
            "intent": Intent.BROWSER_CONTROL,
            "plan": [
                {"action": "WINDOWS_SHORTCUT", "payload": command},
                {"action": "RESPONSE", "payload": "Done."}
            ],
            "response": "Done.",
            "blocked": False,
            "reason": ""
        }
    
    def _handle_type_text(self, text: str) -> dict:
        """Handle typing text"""
        return {
            "intent": Intent.TYPE_TEXT,
            "plan": [
                {"action": "TYPE_STRING", "payload": text},
                {"action": "RESPONSE", "payload": "Typed."}
            ],
            "response": "Typed.",
            "blocked": False,
            "reason": ""
        }
    
    def _handle_unknown(self, user_input: str) -> dict:
        """Handle unknown input - ask for clarification"""
        return {
            "intent": Intent.UNKNOWN,
            "plan": [],
            "response": "Not sure what you mean. Can you be more specific?",
            "blocked": True,
            "reason": "unclear_intent"
        }
    
    def confirm_risky_action(self, action: str) -> dict:
        """Execute a previously blocked risky action after confirmation"""
        return {
            "intent": Intent.SYSTEM_CONTROL,
            "plan": [
                {"action": "WINDOWS_SHORTCUT", "payload": action},
                {"action": "RESPONSE", "payload": "Confirmed and executed."}
            ],
            "response": "Confirmed and executed.",
            "blocked": False,
            "reason": ""
        }


# =============================================================================
# SINGLETON INSTANCE
# =============================================================================

_sentinel_instance = None

def get_sentinel() -> SentinelCore:
    """Get or create the singleton SentinelCore instance"""
    global _sentinel_instance
    if _sentinel_instance is None:
        _sentinel_instance = SentinelCore()
    return _sentinel_instance

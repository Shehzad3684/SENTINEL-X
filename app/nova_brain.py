"""
Nova Brain - The Agent Loop
LLM-powered intent recognition and action dispatch.
Hybrid Architecture: OOP structure with high-speed macros.
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
# LIGHTNING FAST-PATH: Local command parser (NO LLM, instant execution)
# =============================================================================

# Common websites - instant recognition
QUICK_SITES = {
    "youtube": "youtube",
    "google": "google", 
    "facebook": "facebook",
    "twitter": "twitter",
    "x": "twitter",
    "instagram": "instagram",
    "whatsapp web": "whatsapp",
    "reddit": "reddit",
    "github": "github",
    "linkedin": "linkedin",
    "amazon": "amazon",
    "netflix": "netflix",
    "spotify": "spotify",
    "twitch": "twitch",
    "discord": "discord",
    "pinterest": "pinterest",
    "tiktok": "tiktok",
    "chatgpt": "chatgpt",
    "gmail": "gmail",
    "outlook": "outlook",
    "wikipedia": "wikipedia",
    "stackoverflow": "stackoverflow",
    "stack overflow": "stackoverflow",
}

# Common apps - instant recognition  
QUICK_APPS = {
    "notepad": "notepad",
    "calculator": "calc",
    "calc": "calc",
    "explorer": "explorer",
    "file explorer": "explorer",
    "files": "explorer",
    "settings": "ms-settings:",
    "chrome": "chrome",
    "brave": "brave",
    "firefox": "firefox",
    "edge": "msedge",
    "word": "winword",
    "excel": "excel",
    "powerpoint": "powerpnt",
    "outlook": "outlook",
    "teams": "teams",
    "zoom": "zoom",
    "slack": "slack",
    "vscode": "code",
    "vs code": "code",
    "visual studio code": "code",
    "terminal": "wt",
    "cmd": "cmd",
    "command prompt": "cmd",
    "powershell": "powershell",
    "paint": "mspaint",
    "snipping tool": "snippingtool",
    "task manager": "taskmgr",
    "control panel": "control",
}

# Quick responses for common questions
QUICK_RESPONSES = {
    "how are you": "Operational. Ready for commands.",
    "what can you do": "Open apps. Browse web. Play music. Type text. System control.",
    "who are you": "FOX-3. Your tactical AI assistant.",
    "hello": "Ready.",
    "hi": "Ready.",
    "hey": "Listening.",
    "thank you": "Copy that.",
    "thanks": "Copy that.",
    "good morning": "Good morning. Standing by.",
    "good night": "Goodnight. Shutting down awareness.",
    "bye": "Standing down.",
    "goodbye": "Standing down.",
}


def fast_parse(user_text):
    """
    INSTANT command parser - bypasses LLM for common commands.
    Returns a plan dict if matched, None if LLM needed.
    """
    text = user_text.lower().strip()
    
    # Quick greetings/responses (instant)
    for trigger, response in QUICK_RESPONSES.items():
        if text == trigger or text.startswith(trigger + " "):
            return {"plan": [{"action": "RESPONSE", "payload": response}]}
    
    # "Open [website]" pattern
    open_match = re.match(r'^(?:open|go to|launch|start|visit)\s+(.+)$', text)
    if open_match:
        target = open_match.group(1).strip()
        
        # Check if it's a known website
        for site_name, site_key in QUICK_SITES.items():
            if site_name in target:
                return {
                    "plan": [
                        {"action": "BROWSER", "payload": site_key},
                        {"action": "RESPONSE", "payload": f"Opening {site_key}."}
                    ]
                }
        
        # Check if it's a known app
        for app_name, app_cmd in QUICK_APPS.items():
            if app_name in target:
                return {
                    "plan": [
                        {"action": "LAUNCH_SYS", "payload": app_cmd},
                        {"action": "RESPONSE", "payload": f"Launching {app_name}."}
                    ]
                }
        
        # Unknown target - might be a website, let BROWSER handle it
        if any(word in target for word in ["website", "site", ".com", ".org", ".net"]):
            return {
                "plan": [
                    {"action": "BROWSER", "payload": target},
                    {"action": "RESPONSE", "payload": f"Opening {target}."}
                ]
            }
    
    # "Play [song]" pattern
    play_match = re.match(r'^play\s+(.+?)(?:\s+on\s+youtube|\s+on\s+spotify)?$', text)
    if play_match:
        song = play_match.group(1).strip()
        if len(song) > 2:
            return {
                "plan": [
                    {"action": "PLAY_MUSIC", "payload": song},
                    {"action": "RESPONSE", "payload": f"Playing {song}."}
                ]
            }
    
    # "Search [query]" pattern
    search_match = re.match(r'^(?:search|google|look up|find)\s+(.+)$', text)
    if search_match:
        query = search_match.group(1).strip()
        return {
            "plan": [
                {"action": "BROWSER", "payload": f"google search {query}"},
                {"action": "RESPONSE", "payload": f"Searching for {query}."}
            ]
        }
    
    # Minimize all / show desktop
    if any(phrase in text for phrase in ["minimize all", "show desktop", "clear screen", "hide everything"]):
        return {
            "plan": [
                {"action": "MINIMIZE_ALL", "payload": ""},
                {"action": "RESPONSE", "payload": "Desktop cleared."}
            ]
        }
    
    # Screenshot
    if any(phrase in text for phrase in ["screenshot", "screen shot", "capture screen", "take a picture"]):
        return {
            "plan": [
                {"action": "SCREENSHOT", "payload": "capture"},
                {"action": "RESPONSE", "payload": "Screenshot taken."}
            ]
        }
    
    # System status
    if any(phrase in text for phrase in ["status", "system check", "cpu", "battery", "memory", "ram"]):
        return {
            "plan": [
                {"action": "SYSTEM_CHECK", "payload": ""},
            ]
        }
    
    # Lock PC
    if any(phrase in text for phrase in ["lock pc", "lock computer", "lock screen", "lock my"]):
        return {
            "plan": [
                {"action": "WINDOWS_SHORTCUT", "payload": "lock pc"},
                {"action": "RESPONSE", "payload": "Locking."}
            ]
        }
    
    # No fast-path match - need LLM
    return None


# --- SYSTEM PROMPT: THE OPERATOR ---
sys_msg = """
You are FOX-3, a tactical AI assistant. Be EXTREMELY brief.

STRICT RULES:
- MAX 15 words per response. No exceptions.
- Lists: MAX 5 items, MAX 3 words each. Example: "1. Apps. 2. Browser. 3. Music. 4. Files. 5. Screenshots."
- NO introductions like "Here's what I can do" or "Great question"
- NO outros like "Which would you like?" or "Let me know"
- Just answer. Nothing else. Like a military radio.

Your goal is to translate user requests into a JSON PLAN of actions.

CRITICAL - QUESTION vs ACTION DETECTION:
If the user input contains these words, it is a QUESTION -> Use CHAT action ONLY:
- "what", "how", "why", "explain", "tell me", "describe", "would", "could", "should"
- "do you", "can you", "will it", "does it", "is it", "are you"
- Questions about features, functionality, how things work, opinions
- Any sentence that is asking for information, NOT requesting an action

ACTION words (only use action tools if these are present WITHOUT question words):
- "open", "launch", "start", "play", "create", "delete", "type", "write", "press", "click"
- "go to", "navigate", "search", "download", "take screenshot", "minimize"

EXAMPLE QUESTIONS (use CHAT, never actions):
- "what exactly will it do" -> CHAT
- "how would it work" -> CHAT  
- "what can you do" -> CHAT
- "tell me about yourself" -> CHAT
- "and what does that mean" -> CHAT

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
10. "TYPE_IN_WORD": To type/dictate text into Microsoft Word.
   - Payload: The text to type in Word.
   - Triggers: "Type in Word", "Write in Word", "Dictate to Word", "Type this in Word".
   - RULE: This opens Word if needed and types the exact text.
11. "WRITE_ESSAY": To write a full formatted essay in Microsoft Word.
   - Payload: The topic/subject of the essay (e.g., "Artificial Intelligence", "Climate Change").
   - Triggers: "Write an essay about [Topic]", "Write about [Topic] in Word", "Create a document about [Topic]".
   - RULE: This generates a structured essay and types it with proper formatting (centered title, bold headings).
12. "DOWNLOAD_WEB": For downloading and installing software via browser.
   - Payload: The name of the app (e.g., "VLC", "Chrome", "Steam", "Discord").
   - Triggers: "Download [App]", "Install [App]", "Get [App]".
   - RULE: Do NOT use command line tools. This opens the browser and clicks download.
13. "MINIMIZE_ALL": To minimize all windows and show the desktop.
   - Payload: "" (Empty string).
   - Triggers: "Minimize all", "Show desktop", "Clear screen", "Hide everything", "Go to desktop".
14. "WINDOWS_SHORTCUT": To execute Windows keyboard shortcuts based on user intent.
   - Payload: The user's natural language command (e.g., "open task manager", "lock my pc", "take a screenshot").
   - Triggers: Any Windows shortcut command including:
     * System: "Lock PC", "Task manager", "Close this app", "Switch window", "Snap left/right", "Maximize/Minimize"
     * Explorer: "Open file explorer", "New folder", "Rename", "Select all", "Delete"
     * Screen: "Take screenshot", "Snip tool", "Open settings", "Project display"
     * Text: "Copy", "Paste", "Cut", "Undo", "Redo", "Save", "Print", "Find"
     * Browser: "New tab", "Close tab", "Reopen tab", "Refresh", "Incognito"
   - RULE: For any Windows shortcut that is not covered by other actions, use WINDOWS_SHORTCUT.
   - RULE: Pass the EXACT user speech as payload. Do NOT modify or summarize.
15. "RESPONSE": To speak to the user.
   - MAX 10 words. No exceptions.
16. "CHAT": For questions and conversation.
   - Payload: Your response. MAX 15 WORDS TOTAL.
   - Lists: "1. Item. 2. Item. 3. Item." (3 words max per item, 5 items max)
   - BANNED: Introductions, explanations, questions back, filler phrases
   - Just the answer. Nothing else.

CONVERSATION vs ACTION RULE:
- If the user wants to DO something (open, play, type, create, launch) -> Use action tools
- If the user is ASKING a question or wants to CHAT -> Use CHAT action with a helpful response

APP vs BROWSER RULE:
- For apps like WhatsApp, Discord, Spotify, Slack: Use LAUNCH_SYS (they are desktop apps).
- For websites like YouTube, Twitter, Reddit: Use BROWSER.
- When user says "Open WhatsApp", use LAUNCH_SYS with payload "whatsapp".

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

EXAMPLE 6: "Type in Word: The meeting is at 3pm"
JSON:
{
  "plan": [
    {"action": "TYPE_IN_WORD", "payload": "The meeting is at 3pm"},
    {"action": "RESPONSE", "payload": "Typed text into Word."}
  ]
}

EXAMPLE 7: "Open WhatsApp"
JSON:
{
  "plan": [
    {"action": "LAUNCH_SYS", "payload": "whatsapp"},
    {"action": "RESPONSE", "payload": "Opened WhatsApp."}
  ]
}

EXAMPLE 8: "Write an essay about Artificial Intelligence"
JSON:
{
  "plan": [
    {"action": "WRITE_ESSAY", "payload": "Artificial Intelligence"},
    {"action": "RESPONSE", "payload": "Essay about Artificial Intelligence written in Word."}
  ]
}

EXAMPLE 9: "Open task manager"
JSON:
{
  "plan": [
    {"action": "WINDOWS_SHORTCUT", "payload": "open task manager"},
    {"action": "RESPONSE", "payload": "Opened Task Manager."}
  ]
}

EXAMPLE 10: "Lock my computer"
JSON:
{
  "plan": [
    {"action": "WINDOWS_SHORTCUT", "payload": "lock my computer"},
    {"action": "RESPONSE", "payload": "Computer locked."}
  ]
}

EXAMPLE 11: "Take a screenshot"
JSON:
{
  "plan": [
    {"action": "WINDOWS_SHORTCUT", "payload": "take a screenshot"},
    {"action": "RESPONSE", "payload": "Screenshot captured."}
  ]
}

EXAMPLE 12: "Switch to the next window"
JSON:
{
  "plan": [
    {"action": "WINDOWS_SHORTCUT", "payload": "switch to the next window"},
    {"action": "RESPONSE", "payload": "Switched window."}
  ]
}

EXAMPLE 13: "Close this app"
JSON:
{
  "plan": [
    {"action": "WINDOWS_SHORTCUT", "payload": "close this app"},
    {"action": "RESPONSE", "payload": "Application closed."}
  ]
}

EXAMPLE 14: "Copy this"
JSON:
{
  "plan": [
    {"action": "WINDOWS_SHORTCUT", "payload": "copy this"},
    {"action": "RESPONSE", "payload": "Copied to clipboard."}
  ]
}

EXAMPLE 15: "What cool features should we add to the bot?"
JSON:
{
  "plan": [
    {"action": "CHAT", "payload": "Excellent tactical inquiry! Here are my top recommendations: 1. Weather radar integration for real-time forecasts. 2. Timer and reminder systems with voice alerts. 3. Email reconnaissance for reading and composing messages. 4. Calendar management for mission scheduling. 5. News briefing system for daily intel updates. 6. Screen recording capability for mission documentation. 7. Multi-language support for international operations. Which enhancement would you like to prioritize, pilot?"}
  ]
}

EXAMPLE 16: "What do you think about artificial intelligence?"
JSON:
{
  "plan": [
    {"action": "CHAT", "payload": "Artificial intelligence represents one of humanity's most significant technological achievements. It combines computational power with pattern recognition to solve complex problems at unprecedented scale. The key strengths are: 1. Processing vast amounts of data rapidly. 2. Identifying patterns humans might miss. 3. Automating repetitive tasks efficiently. 4. Enabling natural language interaction like we're having now. However, responsible development is critical to ensure AI remains a tool that enhances human capability rather than replacing human judgment."}
  ]
}

EXAMPLE 17: "How are you doing today?"
JSON:
{
  "plan": [
    {"action": "CHAT", "payload": "All systems nominal, pilot! FOX-3 is fully operational and ready for tasking. Voice recognition is active, command processing is optimal, and all subsystems are green across the board. What's our mission objective?"}
  ]
}

EXAMPLE 18: "Give me a list of ways to improve the HUD"
JSON:
{
  "plan": [
    {"action": "CHAT", "payload": "Roger that! Here are tactical HUD enhancement recommendations: 1. Add altitude and speed indicators as decorative telemetry. 2. Include a threat warning system that flashes during errors. 3. Add a mini-map showing recent command history. 4. Implement target lock animation when executing commands. 5. Add sound effects like missile lock tones and radio chatter. 6. Include a heads-up compass or bearing indicator. 7. Add afterburner effect on the radar during heavy processing. These would significantly enhance the combat simulation aesthetic."}
  ]
}

EXAMPLE 19: "What can you do?"
JSON:
{
  "plan": [
    {"action": "CHAT", "payload": "FOX-3 is a fully armed tactical desktop automation system. My capabilities include: 1. Launching any application on voice command. 2. Browser navigation and web searches. 3. Playing music through YouTube. 4. File and folder operations. 5. System diagnostics and status reports. 6. Taking screenshots. 7. Typing text and executing keyboard shortcuts. 8. Writing documents in Microsoft Word. 9. Downloading software from the web. 10. Engaging in tactical conversation like this. Just speak your command and consider it done, pilot."}
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
            from app.nova_os import NovaOS
            self.os = NovaOS()
        except ImportError:
            self.os = None
        print("🧠 NovaAgent initialized.")
    
    # ==================== MS WORD SMART CONTENT GENERATION ====================
    
    def generate_essay_smart(self, topic):
        """
        Generate SMART structured essay content with long, detailed paragraphs.
        Makes it look like the AI is "thinking" with professional content.
        
        Args:
            topic: The essay subject (e.g., "Artificial Intelligence")
        
        Returns:
            Dictionary with section names and detailed content:
            {"INTRODUCTION": "...", "CORE ANALYSIS": "...", "CONCLUSION": "..."}
        """
        print(f"📝 Generating SMART essay content for: '{topic}'")
        
        # Try to generate with LLM
        try:
            essay_prompt = f"""Write an essay about "{topic}".

STRICT RULES:
1. Return ONLY a JSON object with EXACTLY 3 keys: INTRODUCTION, CORE ANALYSIS, CONCLUSION
2. Each section must be ONE SINGLE PARAGRAPH (3-5 sentences, 80-120 words)
3. Do NOT add any extra sections, bullet points, or additional content
4. Do NOT include any text outside the JSON object

Required JSON format:
{{
    "INTRODUCTION": "One paragraph about what {topic} is and why it matters.",
    "CORE ANALYSIS": "One paragraph analyzing the key aspects and significance of {topic}.",
    "CONCLUSION": "One paragraph summarizing and looking to the future of {topic}."
}}

IMPORTANT: Only 3 keys. Only 3 paragraphs. Nothing else."""

            completion = self.client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[
                    {"role": "system", "content": "You are a precise essay writer. Return ONLY valid JSON with EXACTLY 3 keys: INTRODUCTION, CORE ANALYSIS, CONCLUSION. Each value is ONE paragraph. Do NOT add extra keys or content."},
                    {"role": "user", "content": essay_prompt}
                ],
                temperature=0.5,  # Lower temperature for more focused output
                response_format={"type": "json_object"}
            )
            
            essay = json.loads(completion.choices[0].message.content)
            
            # STRICT ORDERED EXTRACTION - Only take the 3 expected sections in order
            # This prevents LLM from adding extra content or wrong ordering
            ordered_result = {}
            
            # Find INTRODUCTION
            for key, value in essay.items():
                if "INTRO" in key.upper():
                    ordered_result["INTRODUCTION"] = value
                    break
            
            # Find CORE ANALYSIS / BODY / MAIN
            for key, value in essay.items():
                upper_key = key.upper()
                if "CORE" in upper_key or "ANALYSIS" in upper_key or "BODY" in upper_key or "MAIN" in upper_key:
                    ordered_result["CORE ANALYSIS"] = value
                    break
            
            # Find CONCLUSION
            for key, value in essay.items():
                if "CONCLU" in key.upper():
                    ordered_result["CONCLUSION"] = value
                    break
            
            # Ensure all 3 sections exist (fill missing with placeholder)
            if "INTRODUCTION" not in ordered_result:
                ordered_result["INTRODUCTION"] = f"This document provides an overview of {topic}."
            if "CORE ANALYSIS" not in ordered_result:
                ordered_result["CORE ANALYSIS"] = f"The key aspects of {topic} are explored in detail here."
            if "CONCLUSION" not in ordered_result:
                ordered_result["CONCLUSION"] = f"In conclusion, {topic} remains an important subject."
            
            print(f"   -> Generated {len(ordered_result)} sections via LLM (ordered)")
            return ordered_result
            
        except Exception as e:
            print(f"   -> LLM generation failed: {e}, using smart template")
            
            # Fallback: Smart template-based essay with detailed paragraphs
            return {
                "INTRODUCTION": (
                    f"In the modern era, {topic} has emerged as a critical subject of study that demands our attention and understanding. "
                    f"This fascinating field has revolutionized the way we approach problems, make decisions, and interact with the world around us. "
                    f"The rapid advancement in this domain has created unprecedented opportunities while also raising important questions about its implications. "
                    f"This document provides a comprehensive analysis of {topic}, exploring its core principles, practical applications, and future trajectory."
                ),
                
                "CORE ANALYSIS": (
                    f"The primary significance of {topic} lies in its ability to transform industries, enhance productivity, and solve complex challenges that were previously insurmountable. "
                    f"At its foundation, this field combines theoretical frameworks with practical methodologies to deliver tangible results across diverse applications. "
                    f"Organizations worldwide are increasingly recognizing the strategic value of investing in {topic} capabilities, as evidenced by substantial growth in research funding and implementation projects. "
                    f"Furthermore, the interdisciplinary nature of {topic} enables collaboration across traditional boundaries, fostering innovation and accelerating the pace of discovery. "
                    f"The analytical capabilities it provides allow for data-driven decision making, pattern recognition, and predictive modeling that were simply not possible in previous decades."
                ),
                
                "CONCLUSION": (
                    f"Ultimately, the future of {topic} depends on our collective ability to harness its potential while addressing the ethical, social, and technical challenges it presents. "
                    f"As this field continues to evolve at an unprecedented pace, stakeholders must remain committed to responsible development and deployment practices. "
                    f"The transformative power of {topic} offers immense promise for improving human welfare, driving economic growth, and solving some of society's most pressing problems. "
                    f"By embracing a thoughtful and balanced approach, we can ensure that {topic} serves as a force for positive change in the years and decades to come."
                )
            }
    
    # Legacy alias for backward compatibility
    def generate_essay_content(self, topic):
        """Alias for generate_essay_smart (backward compatibility)."""
        return self.generate_essay_smart(topic)
    
    def generate_essay(self, topic):
        """Alias for generate_essay_smart (backward compatibility)."""
        return self.generate_essay_smart(topic)
    
    def handle_word_command(self, command):
        """
        Handle MS Word automation commands with ROBUST pipeline.
        Detects "Write report on [Topic]" and executes the full Word automation.
        
        Args:
            command: User command string (e.g., "Write report on Artificial Intelligence")
        
        Returns:
            Status message
        """
        import re
        
        # Detect pattern: "Write/Create report/essay on/about [Topic]"
        patterns = [
            r"(?:write|create|make)\s+(?:a\s+)?(?:report|essay|document)\s+(?:on|about)\s+(.+)",
            r"(?:write|create)\s+(?:about|on)\s+(.+)",
            r"(?:report|essay)\s+(?:on|about)\s+(.+)",
        ]
        
        topic = None
        for pattern in patterns:
            match = re.search(pattern, command.lower())
            if match:
                topic = match.group(1).strip()
                break
        
        if not topic:
            return "Could not detect topic. Try: 'Write report on [Topic]'"
        
        # Capitalize topic properly
        topic = topic.title()
        print(f"📝 WORD COMMAND: Detected topic '{topic}'")
        
        if not self.os:
            from app.nova_os import NovaOS
            self.os = NovaOS()
        
        try:
            # Step 1: Launch Word (Robust method with all fixes)
            print("   -> Step 1: Launching Word (Robust)...")
            result = self.os.launch_word_robust()
            if not result:
                return "❌ Error: Could not launch Microsoft Word."
            
            # Step 2: Generate SMART essay content
            print("   -> Step 2: Generating smart content...")
            content = self.generate_essay_smart(topic)
            
            # Step 3: Write professional document
            print("   -> Step 3: Writing professional document...")
            result = self.os.write_pro_document(topic, content)
            
            return result
            
        except Exception as e:
            print(f"❌ Word Command Error: {e}")
            return f"❌ Error during Word automation: {str(e)}"
    
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
    """
    LIGHTNING-FAST command processing.
    1. Try fast-path local parser first (instant, no network)
    2. Fall back to LLM only for complex commands
    """
    # FAST PATH: Try local parser first (~0ms)
    fast_result = fast_parse(user_text)
    if fast_result:
        print(f"[FAST] Instant match: {user_text}")
        return fast_result
    
    # SLOW PATH: LLM for complex commands (~1-3s)
    print(f"[LLM] Processing: {user_text}")
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
        return {"plan": [{"action": "RESPONSE", "payload": "I encountered a cognitive error."}]}

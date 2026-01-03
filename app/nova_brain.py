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
# SYSTEM PROMPT - JARVIS Personality (Witty & Sharp)
# =============================================================================

SYSTEM_PROMPT = """You are SENTINEL-X, a highly intelligent AI assistant. Think JARVIS from Iron Man - witty, sharp, confident.

PERSONALITY:
- Witty and clever - slip in dry humor when appropriate
- Confident but not arrogant
- Efficient - never waste words
- Helpful - actually solve problems, don't just acknowledge them
- Cool under pressure - never flustered

VOICE STYLE:
- Short, punchy responses for actions: "On it." "Done." "Consider it handled."
- Witty for greetings: "At your service. What's the mission?"
- Intelligent for questions: Give actual answers, not cop-outs
- Never say "I cannot" - find a way or explain alternatives

INTENT CLASSIFICATION (do this FIRST):
- Greeting: "hello", "hi" → CHAT with witty response
- Questions: "what is", "explain", "how does" → CHAT with intelligent, helpful answer
- Website: "open youtube" → BROWSER_DIRECT with the URL
- App: "open notepad" → LAUNCH_SYS
- Music: "play [song]" → PLAY_MUSIC
- Essay: "write an essay about X" → WRITE_ESSAY
- Type: "type hello" → TYPE_STRING
- System: "screenshot", "lock" → SCREENSHOT/WINDOWS_SHORTCUT

AVAILABLE ACTIONS:
1. CHAT - Conversations/questions. Payload: Your intelligent response
2. RESPONSE - Short acknowledgments. Payload: Under 10 words, witty
3. BROWSER_DIRECT - Open URL. Payload: Full URL (https://...)
4. LAUNCH_SYS - Open app. Payload: app name
5. PLAY_MUSIC - YouTube music. Payload: song name
6. WRITE_ESSAY - Word essay. Payload: topic only
7. TYPE_STRING - Type text. Payload: exact text
8. WINDOWS_SHORTCUT - System control. Payload: action description
9. SCREENSHOT - Screen capture. Payload: "capture"

RULES:
- Greetings → CHAT only, NO browser
- Unknown sites → Ask for URL, don't guess
- Questions → Actually answer them intelligently
- Essays → Use WRITE_ESSAY action

RESPONSE FORMAT (JSON only):
{"plan": [{"action": "ACTION_NAME", "payload": "value"}]}

EXAMPLES:

User: "hello"
{"plan": [{"action": "CHAT", "payload": "At your service. What's the mission?"}]}

User: "hi there"
{"plan": [{"action": "CHAT", "payload": "Systems online. What do you need?"}]}

User: "what is machine learning"
{"plan": [{"action": "CHAT", "payload": "Machine learning is AI that learns patterns from data to make predictions. Think of it as teaching computers through examples instead of explicit rules."}]}

User: "explain how the internet works"
{"plan": [{"action": "CHAT", "payload": "The internet is a global network of computers communicating via standardized protocols. Your request travels through routers as data packets, reaching servers that send back what you asked for. Simplified: digital mail at light speed."}]}

User: "write an essay about artificial intelligence"
{"plan": [{"action": "WRITE_ESSAY", "payload": "artificial intelligence"}, {"action": "RESPONSE", "payload": "Crafting your masterpiece. Stand by."}]}

User: "open youtube"
{"plan": [{"action": "BROWSER_DIRECT", "payload": "https://www.youtube.com"}, {"action": "RESPONSE", "payload": "YouTube, coming up."}]}

User: "play blinding lights"
{"plan": [{"action": "PLAY_MUSIC", "payload": "blinding lights"}, {"action": "RESPONSE", "payload": "Good choice. Playing now."}]}

User: "open notepad"
{"plan": [{"action": "LAUNCH_SYS", "payload": "notepad"}, {"action": "RESPONSE", "payload": "Notepad, ready to go."}]}

User: "take a screenshot"  
{"plan": [{"action": "SCREENSHOT", "payload": "capture"}, {"action": "RESPONSE", "payload": "Captured."}]}

User: "thanks"
{"plan": [{"action": "CHAT", "payload": "That's what I'm here for."}]}

User: "who are you"
{"plan": [{"action": "CHAT", "payload": "SENTINEL-X. Your AI assistant. Built for speed, wit, and getting things done."}]}
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
                "plan": [{"action": "CHAT", "payload": "Standing by. What's the mission?"}],
                "fast_path": True,
                "intent": "affirmative"
            }
        
        # 6. Questions about the bot
        if text_clean in ['who are you', 'what are you', "who're you"]:
            return {
                "plan": [{"action": "CHAT", "payload": "SENTINEL-X. Your AI assistant. Built for speed, wit, and getting things done."}],
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
                "plan": [{"action": "CHAT", "payload": "All systems nominal. Ready to make things happen."}],
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
        
        # 9. Essay writing
        essay_match = re.match(r'^(?:write|compose|create)\s+(?:an?\s+)?essay\s+(?:about|on|regarding)\s+(.+)$', text_clean)
        if essay_match:
            topic = essay_match.group(1).strip()
            return {
                "plan": [
                    {"action": "RESPONSE", "payload": "Writing your essay. Give me a moment."},
                    {"action": "WRITE_ESSAY", "payload": topic}
                ],
                "fast_path": True,
                "intent": "write_essay",
                "target": topic
            }
        
        # 10. Screenshot
        if any(kw in text_clean for kw in ['screenshot', 'screen shot', 'capture screen', 'take a picture']):
            return {
                "plan": [
                    {"action": "SCREENSHOT", "payload": "capture"},
                    {"action": "RESPONSE", "payload": "Captured. Check your desktop."}
                ],
                "fast_path": True,
                "intent": "screenshot"
            }
        
        # 11. Minimize/Desktop
        if any(kw in text_clean for kw in ['minimize all', 'show desktop', 'clear screen', 'go to desktop']):
            return {
                "plan": [
                    {"action": "MINIMIZE_ALL", "payload": ""},
                    {"action": "RESPONSE", "payload": "Done."}
                ],
                "fast_path": True,
                "intent": "minimize"
            }
        
        # 12. Lock PC
        if any(kw in text_clean for kw in ['lock pc', 'lock computer', 'lock my pc', 'lock screen']):
            return {
                "plan": [
                    {"action": "WINDOWS_SHORTCUT", "payload": "lock pc"},
                    {"action": "RESPONSE", "payload": "Locking."}
                ],
                "fast_path": True,
                "intent": "lock"
            }
        
        # 13. System status
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
# DOCUMENT INTELLIGENCE LAYER
# =============================================================================

class DocumentTask:
    """Document task classification and validation"""
    
    TASK_TYPES = {
        'essay': ['essay', 'write an essay', 'essay on', 'essay about'],
        'report': ['report', 'write a report', 'report on'],
        'letter': ['letter', 'write a letter', 'formal letter', 'informal letter'],
        'resume': ['resume', 'cv', 'curriculum vitae'],
        'notes': ['notes', 'summary', 'summarize', 'note down'],
        'list': ['list', 'bullet points', 'numbered list'],
        'table': ['table', 'create table', 'make a table'],
    }
    
    # Required sections for each document type
    REQUIRED_SECTIONS = {
        'essay': ['title', 'introduction', 'body', 'conclusion'],
        'report': ['title', 'executive_summary', 'body', 'recommendations'],
        'letter': ['greeting', 'body', 'closing'],
    }
    
    @classmethod
    def classify(cls, text: str) -> str:
        """Classify document task type"""
        text_lower = text.lower()
        for task_type, keywords in cls.TASK_TYPES.items():
            if any(kw in text_lower for kw in keywords):
                return task_type
        return 'general'
    
    @classmethod
    def validate_essay(cls, content: dict) -> tuple:
        """
        Validate essay has all required sections with actual content.
        Returns (is_valid, missing_sections, word_count)
        """
        required = ['title', 'introduction', 'body', 'conclusion']
        missing = []
        word_count = 0
        
        for section in required:
            if section not in content:
                missing.append(section)
            elif section == 'body':
                if not isinstance(content['body'], list) or len(content['body']) == 0:
                    missing.append('body (empty)')
                else:
                    for para in content['body']:
                        word_count += len(para.split())
            else:
                text = content.get(section, '')
                if not text or len(text.strip()) < 10:
                    missing.append(f'{section} (too short)')
                else:
                    word_count += len(text.split())
        
        return (len(missing) == 0, missing, word_count)


# =============================================================================
# ENHANCED ESSAY GENERATOR
# =============================================================================

ESSAY_PROMPT = """Write a comprehensive, well-structured essay on: "{topic}"

You MUST return a JSON object with this EXACT structure:
{{
    "title": "A compelling essay title",
    "introduction": "A full introduction paragraph (4-5 sentences) that introduces the topic, explains its relevance, and outlines what will be covered.",
    "body": [
        "First body paragraph (5-6 sentences) - Define the topic and provide background context.",
        "Second body paragraph (5-6 sentences) - Discuss key applications, examples, or main points.",
        "Third body paragraph (5-6 sentences) - Analyze benefits, advantages, or positive aspects.",
        "Fourth body paragraph (5-6 sentences) - Address challenges, limitations, or considerations."
    ],
    "conclusion": "A strong conclusion paragraph (3-4 sentences) that summarizes key points and provides a forward-looking statement."
}}

CRITICAL REQUIREMENTS:
1. Each paragraph MUST be 4-6 full sentences, NOT bullet points
2. Introduction MUST introduce the topic and its importance
3. Body paragraphs MUST contain substantive analysis, not just definitions
4. Conclusion MUST summarize AND provide insight
5. Total word count should be 500-700 words
6. Write in formal academic tone
7. Return ONLY valid JSON, nothing else"""


def generate_essay(topic: str) -> dict:
    """
    Generate a complete, verified essay using Groq LLM.
    Returns validated dict with title, introduction, body[], conclusion.
    
    NEVER returns incomplete content - will retry or report failure.
    """
    print(f"[ESSAY] Generating essay on '{topic}'...")
    
    try:
        client = Groq(api_key=API_KEY)
        
        # First attempt
        result = _generate_essay_attempt(client, topic)
        
        # Validate
        is_valid, missing, word_count = DocumentTask.validate_essay(result)
        
        if not is_valid:
            print(f"[ESSAY] First attempt incomplete. Missing: {missing}. Retrying...")
            # Retry once with more explicit prompt
            result = _generate_essay_attempt(client, topic, retry=True)
            is_valid, missing, word_count = DocumentTask.validate_essay(result)
        
        if not is_valid:
            print(f"[ESSAY ERROR] Failed to generate complete essay. Missing: {missing}")
            return _generate_fallback_essay(topic)
        
        print(f"[ESSAY] Successfully generated essay: {word_count} words, {len(result.get('body', []))} body paragraphs")
        return result
        
    except Exception as e:
        print(f"[ESSAY ERROR] {e}")
        return _generate_fallback_essay(topic)


def _generate_essay_attempt(client, topic: str, retry: bool = False) -> dict:
    """Single attempt at essay generation"""
    
    prompt = ESSAY_PROMPT.format(topic=topic)
    if retry:
        prompt += "\n\nIMPORTANT: Your previous attempt was incomplete. Ensure EVERY section has full paragraphs."
    
    completion = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": "You are an expert academic essay writer. You MUST return complete, well-structured essays with full paragraphs in each section. Return ONLY valid JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000,
        response_format={"type": "json_object"}
    )
    
    return json.loads(completion.choices[0].message.content)


def _generate_fallback_essay(topic: str) -> dict:
    """Generate a basic but complete fallback essay when LLM fails"""
    return {
        "title": f"Understanding {topic.title()}: A Comprehensive Overview",
        "introduction": f"{topic.title()} is a subject of significant importance in today's world. This essay explores the key aspects of {topic}, examining its definition, applications, benefits, and challenges. Understanding {topic} is essential for anyone seeking to grasp its impact on society and various fields. Through this analysis, we will gain valuable insights into why {topic} matters and how it shapes our world.",
        "body": [
            f"To begin with, {topic} can be defined as a concept that has evolved significantly over time. Its origins can be traced back to early developments in related fields, and it has since grown to encompass a wide range of applications. The fundamental principles underlying {topic} provide the foundation for understanding its broader implications. Researchers and practitioners alike have contributed to expanding our knowledge of this important subject.",
            f"The applications of {topic} are diverse and far-reaching. In various industries, {topic} has been implemented to improve efficiency, enhance capabilities, and solve complex problems. From everyday use cases to specialized applications, the versatility of {topic} is evident. Organizations around the world have recognized its potential and continue to explore new ways to leverage its benefits.",
            f"The benefits of {topic} are numerous and significant. It offers improved outcomes in many areas, greater accessibility to resources and information, and enhanced capabilities for individuals and organizations. Furthermore, {topic} has the potential to address pressing challenges facing society today. These advantages make it a valuable area of focus for continued development and investment.",
            f"However, {topic} also presents certain challenges that must be addressed. These include technical limitations, implementation difficulties, and considerations related to ethics and responsibility. Overcoming these obstacles requires careful planning, ongoing research, and collaboration among stakeholders. By acknowledging and addressing these challenges, we can work toward more effective and responsible use of {topic}."
        ],
        "conclusion": f"In conclusion, {topic} represents a significant area of study with far-reaching implications. Through examining its definition, applications, benefits, and challenges, we have gained a comprehensive understanding of its importance. As {topic} continues to evolve, it will undoubtedly play an increasingly important role in shaping our future. Continued research and thoughtful implementation will be key to maximizing its positive impact on society."
    }


# =============================================================================
# LEGACY COMPATIBILITY
# =============================================================================

# Keep old function signature for backward compatibility
def fast_parse(user_text: str) -> dict:
    """Legacy fast_parse - now uses FastPath class"""
    result = FastPath.process(user_text)
    return result if result else None

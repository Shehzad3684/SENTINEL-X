"""
Auto-BOT Main Logic
Voice-controlled desktop automation with callback-based architecture.
Designed to be called from GUI without blocking.

LIGHTNING-FAST TTS SYSTEM:
- Windows SAPI for instant responses (~20ms latency)
- Edge-TTS fallback for quality when needed
- Pre-cached common phrases
- Non-blocking async architecture
"""

import asyncio
import threading
import os
import speech_recognition as sr
import edge_tts
import pygame
import win32com.client
import pythoncom
from concurrent.futures import ThreadPoolExecutor

from app import nova_brain, nova_os, get_runtime_audio_file, get_runtime_audio_dir


# ============================================================
# LIGHTNING-FAST TTS ENGINE
# ============================================================

class InstantTTS:
    """
    Ultra-fast text-to-speech using Windows SAPI.
    Latency: ~20ms (vs 500-1000ms for Edge-TTS)
    """
    
    # Common responses to pre-optimize
    SHORT_RESPONSES = {
        "done", "ok", "opened", "created", "deleted", "error", 
        "listening", "processing", "executing", "complete",
        "yes", "no", "starting", "stopping", "ready"
    }
    
    def __init__(self, rate=4):
        """
        Initialize SAPI voice.
        rate: -10 (slowest) to 10 (fastest), default 4 for snappy responses
        """
        self.rate = rate
        self._executor = ThreadPoolExecutor(max_workers=1)
        self._speaker = None
    
    def _init_sapi(self):
        """Initialize SAPI in the current thread (COM requirement)."""
        pythoncom.CoInitialize()
        speaker = win32com.client.Dispatch("SAPI.SpVoice")
        speaker.Rate = self.rate
        
        # Try to get a better voice if available
        voices = speaker.GetVoices()
        for i in range(voices.Count):
            voice = voices.Item(i)
            name = voice.GetDescription()
            # Prefer Zira (female) or David (male) - clearer than default
            if "Zira" in name or "David" in name:
                speaker.Voice = voice
                break
        
        return speaker
    
    def _speak_sync(self, text):
        """Synchronous SAPI speak (runs in thread pool)."""
        try:
            pythoncom.CoInitialize()
            speaker = win32com.client.Dispatch("SAPI.SpVoice")
            speaker.Rate = self.rate
            speaker.Speak(text)
            pythoncom.CoUninitialize()
        except Exception as e:
            print(f"SAPI Error: {e}")
    
    def speak(self, text):
        """
        Instant non-blocking speak.
        Returns immediately, audio plays in background.
        """
        # Fire and forget - don't wait
        self._executor.submit(self._speak_sync, text)
    
    def speak_wait(self, text):
        """Blocking speak - waits for completion."""
        self._speak_sync(text)
    
    def is_short(self, text):
        """Check if text should use instant TTS."""
        if not text:
            return False
        words = text.lower().split()
        # Short = under 10 words OR contains common short response
        return len(words) <= 10 or any(w in self.SHORT_RESPONSES for w in words)


# Global instant TTS engine
_instant_tts = None

def get_instant_tts():
    """Get or create the global instant TTS engine."""
    global _instant_tts
    if _instant_tts is None:
        _instant_tts = InstantTTS(rate=1)  # Slower for clarity (was 4)
    return _instant_tts


class NovaBotEngine:
    """
    Main bot engine that handles voice recognition and command execution.
    Designed to run in a background thread with status callbacks.
    """
    
    def __init__(self, status_callback=None, log_callback=None):
        """
        Initialize the bot engine.
        
        Args:
            status_callback: Function to call when status changes (e.g., "Listening", "Processing")
            log_callback: Function to call for log messages
        """
        self.status_callback = status_callback or (lambda s: None)
        self.log_callback = log_callback or (lambda m: print(m))
        
        self._running = False
        self._thread = None
        self._loop = None
        
        # Audio setup
        self._init_audio()
        
        # Speech recognition setup
        self.recognizer = sr.Recognizer()
        self.recognizer.pause_threshold = 1.0  # Faster response
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        self.log("NovaBotEngine initialized - LIGHTNING MODE")
    
    def _init_audio(self):
        """Initialize pygame mixer for audio playback with minimal latency."""
        try:
            # Smaller buffer = lower latency (256 vs default 512)
            pygame.mixer.init(frequency=24000, buffer=256)
            self.log("Audio system initialized (low-latency mode).")
        except Exception as e:
            self.log(f"Audio init error: {e}")
        
        # Initialize instant TTS
        self.instant_tts = get_instant_tts()
        self.log("Instant TTS engine ready.")
    
    def log(self, message):
        """Log a message via callback."""
        self.log_callback(message)
    
    def set_status(self, status):
        """Update status via callback."""
        self.status_callback(status)
    
    async def speak(self, text):
        """
        LIGHTNING-FAST TTS - Hybrid approach:
        - Short responses (<10 words): Windows SAPI (~20ms)
        - Longer responses: Edge-TTS streaming (better quality)
        """
        if not text:
            return
        
        self.log(f"FOX-3: {text}")
        
        # INSTANT PATH: Short responses use Windows SAPI
        if self.instant_tts.is_short(text):
            # Fire and forget - returns immediately
            self.instant_tts.speak(text)
            # Small delay to let audio start
            await asyncio.sleep(0.05)
            return
        
        # QUALITY PATH: Longer responses use Edge-TTS
        await self._speak_edge_tts(text)
    
    async def _speak_edge_tts(self, text):
        """Edge-TTS for longer, quality responses."""
        try:
            audio_file = get_runtime_audio_file("response.mp3")
            
            # Clear voice at natural speed
            comm = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+10%")
            
            # Stream directly to file
            with open(audio_file, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
            
            if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                return
            
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.03)  # Faster polling
            
            pygame.mixer.music.unload()
            
        except Exception as e:
            self.log(f"TTS Error: {e}")
    
    def speak_instant(self, text):
        """
        SYNCHRONOUS instant speak - for confirmations.
        Use this for immediate feedback like "Done", "Opening", etc.
        """
        if text:
            self.instant_tts.speak(text)
    
    async def _listen_and_execute(self):
        """Main listening and execution loop - LIGHTNING FAST."""
        self.log("\n" + "="*50)
        self.log("AUTO-BOT v2.0 - LIGHTNING MODE")
        self.log("="*50)
        
        while self._running:
            try:
                # LISTENING MODE
                self.set_status("Listening...")
                
                with sr.Microphone() as source:
                    self.log("LISTENING... (Speak your command)")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.3)  # Faster
                    
                    try:
                        audio = self.recognizer.listen(source, timeout=10)
                        self.log("PROCESSING...")
                        self.set_status("Processing...")
                    except sr.WaitTimeoutError:
                        self.log("Timeout. Waiting...")
                        continue
                
                # Check if still running before processing
                if not self._running:
                    break
                
                # RECOGNITION
                try:
                    user_text = self.recognizer.recognize_google(audio)
                    self.log(f"Heard: \"{user_text}\"")
                except sr.UnknownValueError:
                    self.log("Could not understand audio.")
                    continue
                except sr.RequestError as e:
                    self.log(f"Network error: {e}")
                    continue
                
                # PLANNING (via LLM)
                self.set_status("Planning...")
                plan_data = nova_brain.get_operator_plan(user_text)
                plan = plan_data.get("plan", [])
                
                # EXECUTION LOOP
                self.set_status("Executing...")
                for step in plan:
                    if not self._running:
                        break
                    
                    result = nova_os.execute_step(step)
                    
                    # INSTANT response
                    if step.get("action") == "RESPONSE":
                        await self.speak(step.get("payload"))
                    
                    # INSTANT chat
                    elif step.get("action") == "CHAT":
                        await self.speak(step.get("payload"))
                    
                    # For system actions, just log confirmation
                    elif result:
                        self.log(f"[OK] {result}")
                
                self.log("\n[READY] Awaiting next command.\n")
                self.set_status("Ready")
                
            except Exception as e:
                self.log(f"[ERROR] {e}")
                self.set_status("Error")
                await asyncio.sleep(1)
        
        self.set_status("Stopped")
        self.log("Bot stopped.")
    
    async def _execute_text_command(self, user_text):
        """Execute a text command directly (for quick actions)."""
        self.log(f"Command: \"{user_text}\"")
        
        # PLANNING (via LLM)
        self.set_status("Planning...")
        plan_data = nova_brain.get_operator_plan(user_text)
        plan = plan_data.get("plan", [])
        
        # EXECUTION LOOP
        self.set_status("Executing...")
        for step in plan:
            result = nova_os.execute_step(step)
            
            # If the step was a verbal response or chat, speak it
            if step.get("action") == "RESPONSE":
                await self.speak(step.get("payload"))
            elif step.get("action") == "CHAT":
                await self.speak(step.get("payload"))
            elif result:
                self.log(f"[OK] {result}")
        
        self.log("Command completed.")
        self.set_status("Listening...")
    
    def execute_command(self, command_text):
        """
        Execute a text command from the GUI (thread-safe).
        This allows quick actions to work without voice input.
        """
        if not self._running:
            self.log("[WARN] Start Nova first to execute commands!")
            return
        
        if self._loop and self._loop.is_running():
            # Schedule the coroutine on the bot's event loop
            asyncio.run_coroutine_threadsafe(
                self._execute_text_command(command_text),
                self._loop
            )
        else:
            self.log("[WARN] Bot event loop not ready.")
    
    def _run_async_loop(self):
        """Run the async event loop in a thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._listen_and_execute())
        except Exception as e:
            self.log(f"[ERROR] Loop error: {e}")
        finally:
            self._loop.close()
            self._loop = None
    
    def start(self):
        """Start the bot in a background thread."""
        if self._running:
            self.log("[WARN] Bot is already running.")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()
        self.log("[LAUNCH] Bot started!")
        self.set_status("Starting...")
    
    def stop(self):
        """Stop the bot gracefully."""
        if not self._running:
            self.log("[WARN] Bot is not running.")
            return
        
        self.log("[STOP] Stopping bot...")
        self._running = False
        
        # Clean up pygame
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        self.set_status("Stopped")
    
    def is_running(self):
        """Check if the bot is currently running."""
        return self._running


# ============================================================
# LEGACY FUNCTIONS (for backward compatibility / direct run)
# ============================================================

async def speak(text):
    """
    LIGHTNING-FAST TTS (legacy function).
    Uses Windows SAPI for instant response.
    """
    if not text:
        return
    
    print(f"FOX-3: {text}")
    
    tts = get_instant_tts()
    
    # Short responses = instant SAPI
    if tts.is_short(text):
        tts.speak(text)
        await asyncio.sleep(0.05)
        return
    
    # Longer responses = Edge-TTS
    try:
        audio_file = get_runtime_audio_file("response.mp3")
        
        comm = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+10%")
        
        with open(audio_file, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            return
        
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.03)
        
        pygame.mixer.music.unload()
        
    except Exception as e:
        print(f"TTS Error: {e}")


async def main():
    """Legacy main function for command-line usage."""
    # Initialize audio with low latency
    pygame.mixer.init(frequency=24000, buffer=256)
    
    # Initialize instant TTS
    tts = get_instant_tts()
    print("Instant TTS ready!")
    
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.2
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    
    print("\n" + "="*50)
    print("AUTO-BOT v2.0 - LIGHTNING MODE")
    print("="*50)
    print("Instant Start - No pre-loading required.")
    print("Press [ENTER] to activate voice command.\n")

    while True:
        try:
            # 1. MANUAL TRIGGER
            input(">> PRESS ENTER TO COMMAND...")
            
            # 2. LISTENING MODE
            with sr.Microphone() as source:
                print("LISTENING... (Speak freely)")
                recognizer.adjust_for_ambient_noise(source, duration=0.3)  # Faster
                try:
                    audio = recognizer.listen(source, timeout=None)
                    print("PROCESSING...")
                except sr.WaitTimeoutError:
                    print("No speech detected.")
                    continue

            # 3. RECOGNITION
            try:
                user_text = recognizer.recognize_google(audio)
                print(f"Heard: \"{user_text}\"")
            except sr.UnknownValueError:
                print("Could not understand audio.")
                continue
            except sr.RequestError:
                print("Network error.")
                continue

            # 4. PLANNING (via LLM)
            plan_data = nova_brain.get_operator_plan(user_text)
            plan = plan_data.get("plan", [])

            # 5. EXECUTION LOOP
            for step in plan:
                result = nova_os.execute_step(step)
                
                # Verbal response - INSTANT
                if step.get("action") == "RESPONSE":
                    await speak(step.get("payload"))
                
                # Chat response - INSTANT
                elif step.get("action") == "CHAT":
                    await speak(step.get("payload"))
                
                # System actions - log confirmation
                elif result:
                    print(f"Done: {result}")

            print("\nREADY.\n")

        except KeyboardInterrupt:
            print("\nExiting Auto-BOT.")
            break
        except Exception as e:
            print(f"Error: {e}")


def run_bot():
    """
    Entry point for GUI to start the bot.
    Returns a NovaBotEngine instance.
    """
    return NovaBotEngine()


# Allow direct execution from command line
if __name__ == "__main__":
    asyncio.run(main())

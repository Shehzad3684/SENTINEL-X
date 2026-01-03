"""
Nova Main - Entry Point
Voice-controlled desktop automation with LIGHTNING-FAST TTS.
"""

import asyncio
import speech_recognition as sr
import edge_tts
import pygame
import nova_brain
import nova_os
import os
import tempfile
from concurrent.futures import ThreadPoolExecutor

# Try to import Windows SAPI for instant TTS
try:
    import win32com.client
    SAPI_AVAILABLE = True
except ImportError:
    SAPI_AVAILABLE = False
    print("[WARN] pywin32 not available - using Edge-TTS only")

# --- INSTANT TTS SYSTEM ---
class InstantTTS:
    """Lightning-fast TTS using Windows SAPI (~20ms latency)."""
    
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        
        if SAPI_AVAILABLE:
            try:
                self.sapi = win32com.client.Dispatch("SAPI.SpVoice")
                self.sapi.Rate = 3  # Fast speech rate
                self.executor = ThreadPoolExecutor(max_workers=1)
                print("[TTS] Windows SAPI initialized - INSTANT MODE")
            except Exception as e:
                self.sapi = None
                print(f"[TTS] SAPI init failed: {e}")
        else:
            self.sapi = None
    
    def speak(self, text):
        """Non-blocking instant speech."""
        if self.sapi:
            self.executor.submit(self._speak_sync, text)
    
    def _speak_sync(self, text):
        """Synchronous SAPI speech."""
        try:
            self.sapi.Speak(text, 1)  # 1 = async flag
        except Exception as e:
            print(f"[TTS] Error: {e}")
    
    def is_short(self, text):
        """Check if text is short enough for instant SAPI."""
        return len(text) < 100

# Global TTS instance
_instant_tts = None

def get_instant_tts():
    global _instant_tts
    if _instant_tts is None:
        _instant_tts = InstantTTS()
    return _instant_tts

# --- AUDIO SETUP ---
pygame.mixer.init(frequency=24000, buffer=256)  # Lower buffer = faster
recognizer = sr.Recognizer()
recognizer.pause_threshold = 1.2 
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

async def speak(text):
    """LIGHTNING-FAST TTS - instant for short, quality for long."""
    if not text:
        return
    
    print(f"FOX-3: {text}")
    
    tts = get_instant_tts()
    
    # Short responses = instant SAPI (~20ms)
    if tts.sapi and tts.is_short(text):
        tts.speak(text)
        await asyncio.sleep(0.05)
        return
    
    # Longer responses = Edge-TTS (quality)
    try:
        audio_file = os.path.join(tempfile.gettempdir(), "fox3_response.mp3")
        comm = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+50%")
        await comm.save(audio_file)
        
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.03)
        
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"[TTS] Error: {e}")

async def main():
    # Initialize instant TTS
    tts = get_instant_tts()
    
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

if __name__ == "__main__":
    asyncio.run(main())
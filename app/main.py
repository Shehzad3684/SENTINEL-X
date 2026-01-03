"""
Auto-BOT Main Logic
Voice-controlled desktop automation with callback-based architecture.
Designed to be called from GUI without blocking.
"""

import asyncio
import threading
import os
import speech_recognition as sr
import edge_tts
import pygame

from app import nova_brain, nova_os, get_runtime_audio_file, get_runtime_audio_dir


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
        self.recognizer.pause_threshold = 1.2
        self.recognizer.energy_threshold = 300
        self.recognizer.dynamic_energy_threshold = True
        
        self.log("🤖 NovaBotEngine initialized.")
    
    def _init_audio(self):
        """Initialize pygame mixer for audio playback."""
        try:
            pygame.mixer.init(frequency=24000, buffer=512)
            self.log("🔊 Audio system initialized.")
        except Exception as e:
            self.log(f"⚠️ Audio init error: {e}")
    
    def log(self, message):
        """Log a message via callback."""
        self.log_callback(message)
    
    def set_status(self, status):
        """Update status via callback."""
        self.status_callback(status)
    
    async def speak(self, text):
        """Ultra-fast text-to-speech using Edge TTS with streaming."""
        if not text:
            return
        
        self.log(f"🗣️ FOX-3: {text}")
        
        try:
            # Ensure audio directory exists
            audio_dir = get_runtime_audio_dir()
            audio_file = get_runtime_audio_file("response.mp3")
            
            # Fast voice with 50% speed boost for rapid tactical comms
            comm = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+50%")
            
            # Stream directly to file for faster generation
            with open(audio_file, "wb") as f:
                async for chunk in comm.stream():
                    if chunk["type"] == "audio":
                        f.write(chunk["data"])
            
            # Verify and play
            if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
                self.log(f"⚠️ TTS file empty")
                return
            
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            while pygame.mixer.music.get_busy():
                await asyncio.sleep(0.05)  # Faster polling
            
            pygame.mixer.music.unload()
            
        except Exception as e:
            self.log(f"⚠️ TTS Error: {e}")
    
    async def _listen_and_execute(self):
        """Main listening and execution loop."""
        self.log("\n" + "="*50)
        self.log("🤖 AUTO-BOT v2.0 - GUI Mode")
        self.log("="*50)
        
        while self._running:
            try:
                # LISTENING MODE
                self.set_status("🎤 Listening...")
                
                with sr.Microphone() as source:
                    self.log("🟢 LISTENING... (Speak your command)")
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                    
                    try:
                        audio = self.recognizer.listen(source, timeout=10)
                        self.log("🟡 PROCESSING...")
                        self.set_status("⏳ Processing...")
                    except sr.WaitTimeoutError:
                        self.log("⏱️ Listening timeout. Waiting for command...")
                        continue
                
                # Check if still running before processing
                if not self._running:
                    break
                
                # RECOGNITION
                try:
                    user_text = self.recognizer.recognize_google(audio)
                    self.log(f"📝 Heard: \"{user_text}\"")
                except sr.UnknownValueError:
                    self.log("❓ Could not understand audio.")
                    continue
                except sr.RequestError as e:
                    self.log(f"❌ Network error: {e}")
                    continue
                
                # PLANNING (via LLM)
                self.set_status("🧠 Planning...")
                plan_data = nova_brain.get_operator_plan(user_text)
                plan = plan_data.get("plan", [])
                
                # EXECUTION LOOP
                self.set_status("⚡ Executing...")
                for step in plan:
                    if not self._running:
                        break
                    
                    result = nova_os.execute_step(step)
                    
                    # If the step was a verbal response or chat, speak it
                    if step.get("action") == "RESPONSE":
                        await self.speak(step.get("payload"))
                    
                    # CHAT action - conversational responses (speak them)
                    elif step.get("action") == "CHAT":
                        await self.speak(step.get("payload"))
                    
                    # For system actions, just log confirmation
                    elif result:
                        self.log(f"✅ {result}")
                
                self.log("\n🔵 READY FOR NEXT COMMAND.\n")
                self.set_status("✅ Ready")
                
            except Exception as e:
                self.log(f"⚠️ Error: {e}")
                self.set_status("⚠️ Error")
                await asyncio.sleep(1)
        
        self.set_status("⏹️ Stopped")
        self.log("👋 Bot stopped.")
    
    async def _execute_text_command(self, user_text):
        """Execute a text command directly (for quick actions)."""
        self.log(f"📝 Command: \"{user_text}\"")
        
        # PLANNING (via LLM)
        self.set_status("🧠 Planning...")
        plan_data = nova_brain.get_operator_plan(user_text)
        plan = plan_data.get("plan", [])
        
        # EXECUTION LOOP
        self.set_status("⚡ Executing...")
        for step in plan:
            result = nova_os.execute_step(step)
            
            # If the step was a verbal response or chat, speak it
            if step.get("action") == "RESPONSE":
                await self.speak(step.get("payload"))
            elif step.get("action") == "CHAT":
                await self.speak(step.get("payload"))
            elif result:
                self.log(f"✅ {result}")
        
        self.log("✅ Command completed.")
        self.set_status("🎤 Listening...")
    
    def execute_command(self, command_text):
        """
        Execute a text command from the GUI (thread-safe).
        This allows quick actions to work without voice input.
        """
        if not self._running:
            self.log("⚠️ Start Nova first to execute commands!")
            return
        
        if self._loop and self._loop.is_running():
            # Schedule the coroutine on the bot's event loop
            asyncio.run_coroutine_threadsafe(
                self._execute_text_command(command_text),
                self._loop
            )
        else:
            self.log("⚠️ Bot event loop not ready.")
    
    def _run_async_loop(self):
        """Run the async event loop in a thread."""
        self._loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self._loop)
        
        try:
            self._loop.run_until_complete(self._listen_and_execute())
        except Exception as e:
            self.log(f"⚠️ Loop error: {e}")
        finally:
            self._loop.close()
            self._loop = None
    
    def start(self):
        """Start the bot in a background thread."""
        if self._running:
            self.log("⚠️ Bot is already running.")
            return
        
        self._running = True
        self._thread = threading.Thread(target=self._run_async_loop, daemon=True)
        self._thread.start()
        self.log("🚀 Bot started!")
        self.set_status("🚀 Starting...")
    
    def stop(self):
        """Stop the bot gracefully."""
        if not self._running:
            self.log("⚠️ Bot is not running.")
            return
        
        self.log("🛑 Stopping bot...")
        self._running = False
        
        # Clean up pygame
        try:
            pygame.mixer.music.stop()
        except:
            pass
        
        self.set_status("⏹️ Stopped")
    
    def is_running(self):
        """Check if the bot is currently running."""
        return self._running


# ============================================================
# LEGACY FUNCTIONS (for backward compatibility / direct run)
# ============================================================

async def speak(text):
    """Ultra-fast TTS with streaming (legacy function)."""
    if not text:
        return
    
    print(f"🗣️ FOX-3: {text}")
    
    try:
        audio_dir = get_runtime_audio_dir()
        audio_file = get_runtime_audio_file("response.mp3")
        
        # Fast voice with 50% speed boost
        comm = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+50%")
        
        # Stream directly to file
        with open(audio_file, "wb") as f:
            async for chunk in comm.stream():
                if chunk["type"] == "audio":
                    f.write(chunk["data"])
        
        if not os.path.exists(audio_file) or os.path.getsize(audio_file) == 0:
            print(f"TTS file empty")
            return
        
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.05)
        
        pygame.mixer.music.unload()
        
    except Exception as e:
        print(f"TTS Error: {e}")


async def main():
    """Legacy main function for command-line usage."""
    # Initialize audio
    pygame.mixer.init(frequency=24000, buffer=512)
    
    recognizer = sr.Recognizer()
    recognizer.pause_threshold = 1.2
    recognizer.energy_threshold = 300
    recognizer.dynamic_energy_threshold = True
    
    print("\n" + "="*50)
    print("🤖 AUTO-BOT v2.0 - Console Mode")
    print("="*50)
    print("⚡ Instant Start - No pre-loading required.")
    print("👉 Press [ENTER] to activate voice command.\n")

    while True:
        try:
            # 1. MANUAL TRIGGER
            input(">> PRESS ENTER TO COMMAND...")
            
            # 2. LISTENING MODE
            with sr.Microphone() as source:
                print("🟢 LISTENING... (Speak freely, I will wait until you finish)")
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    audio = recognizer.listen(source, timeout=None)
                    print("🟡 PROCESSING...")
                except sr.WaitTimeoutError:
                    print("❌ No speech detected. Returning to standby.")
                    continue

            # 3. RECOGNITION
            try:
                user_text = recognizer.recognize_google(audio)
                print(f"📝 Instruction: \"{user_text}\"")
            except sr.UnknownValueError:
                print("❌ Could not understand audio.")
                continue
            except sr.RequestError:
                print("❌ Network error.")
                continue

            # 4. PLANNING (via LLM)
            plan_data = nova_brain.get_operator_plan(user_text)
            plan = plan_data.get("plan", [])

            # 5. EXECUTION LOOP
            for step in plan:
                result = nova_os.execute_step(step)
                
                # If the step was a verbal response, speak it
                if step.get("action") == "RESPONSE":
                    await speak(step.get("payload"))
                
                # CHAT action - conversational responses (speak them)
                elif step.get("action") == "CHAT":
                    await speak(step.get("payload"))
                
                # For system actions, just log confirmation
                elif result:
                    print(f"✅ {result}")

            print("\n🔴 MISSION COMPLETE. STANDBY.\n")

        except KeyboardInterrupt:
            print("\n👋 Exiting Auto-BOT.")
            break
        except Exception as e:
            print(f"⚠️ SYSTEM ERROR: {e}")


def run_bot():
    """
    Entry point for GUI to start the bot.
    Returns a NovaBotEngine instance.
    """
    return NovaBotEngine()


# Allow direct execution from command line
if __name__ == "__main__":
    asyncio.run(main())

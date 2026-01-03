"""
Nova Main - Entry Point
Voice-controlled desktop automation with OOP architecture.
"""

import asyncio
import speech_recognition as sr
import edge_tts
import pygame
import nova_brain
import nova_os  # NEW: OOP Execution Engine

# --- AUDIO SETUP ---
# Low latency buffer and standard frequency
pygame.mixer.init(frequency=24000, buffer=512)
recognizer = sr.Recognizer()
# High pause_threshold to prevent cutting off the user while thinking
recognizer.pause_threshold = 1.2 
recognizer.energy_threshold = 300
recognizer.dynamic_energy_threshold = True

async def speak(text):
    """Fast, non-blocking TTS."""
    if not text: return
    print(f"🗣️ NOVA: {text}")
    try:
        # Speed up the voice by 25% for a snappier response
        comm = edge_tts.Communicate(text, "en-GB-RyanNeural", rate="+25%")
        await comm.save("response.mp3")
        pygame.mixer.music.load("response.mp3")
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            await asyncio.sleep(0.1)
        pygame.mixer.music.unload()
    except Exception as e:
        print(f"TTS Error: {e}")

async def main():
    print("\n" + "="*50)
    print("🤖 NOVA OPERATOR v2.0 - OOP ARCHITECTURE")
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
                # Clear buffer
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    # timeout=None means it waits indefinitely for speech to start
                    # phrase_time_limit=None means it listens indefinitely until silence
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

            # 5. EXECUTION LOOP (via OOP Engine)
            for step in plan:
                result = nova_os.execute_step(step)  # NEW: Uses NovaOS
                
                # If the step was a verbal response, speak it
                if step.get("action") == "RESPONSE":
                    await speak(step.get("payload"))
                
                # For system actions, just log confirmation
                elif result:
                    print(f"✅ {result}")

            print("\n🔴 MISSION COMPLETE. STANDBY.\n")

        except KeyboardInterrupt:
            print("\n👋 Exiting Nova Operator.")
            break
        except Exception as e:
            print(f"⚠️ SYSTEM ERROR: {e}")

if __name__ == "__main__":
    asyncio.run(main())
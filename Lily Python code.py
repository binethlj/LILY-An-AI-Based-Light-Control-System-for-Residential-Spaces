# ================= FULL FINAL LILY AI SYSTEM =================

import json
from pydoc import text
from unittest import result
import sounddevice as sd
import numpy as np
import time
import serial
import pyttsx3
import threading
import re
import sys
import random
import requests
import noisereduce as nr

from pynput import keyboard
from vosk import Model, KaldiRecognizer
from scipy.signal import resample_poly

# ================= CONFIG =================
MIC_DEVICE_INDEX = x

VOSK_MODEL_PATH = r"E:\Python\vosk-model-small-en-us-0.15

ARDUINO_PORT = "COM"
ARDUINO_BAUD = 9600

MIC_SAMPLE_RATE = 48000
VOSK_SAMPLE_RATE = 16000

# ================= WAKE WORDS =================
WAKE_WORDS = [
    "hey lily",
    "hello lily",
    "lily",
    "hailey",
    "highly",
    "lilly"
]

WAKE_TIMEOUT = 10

sd.default.device = MIC_DEVICE_INDEX

# ================= STATES =================
push_to_talk = False
shift_held = False

wake_mode = False
wake_timer = 0

recorded_audio = []

living1_brightness = 0
living2_brightness = 0

bedroom1_brightness = 0
bedroom2_brightness = 0

waiting_for_relax_choice = False
waiting_for_focus_choice = False
waiting_for_nap_confirmation = False

# ================= TIME =================
current_hour = 12
current_minute = 0

time_set = False

sleep_mode_active = False
away_mode_active = False
morning_reminder_given = False

# ================= MEMORY =================
previous_living1 = 0
previous_living2 = 0

previous_bedroom1 = 0
previous_bedroom2 = 0

previous_outdoor_state = False
previous_panel_state = False

outdoor_is_on = False
panel_is_on = False

# ================= UNKNOWN RESPONSES =================
UNKNOWN_RESPONSES = [
    "I didn't quite catch that sir.",
    "I'm not sure what you mean sir.",
    "Could you say that differently sir?",
    "I don't understand that yet sir.",
    "Sorry sir, I couldn't understand that."
]

# ================= DIRECT COMMANDS =================
DIRECT_COMMAND_KEYWORDS = [
    "living",
    "bedroom",
    "bathroom",
    "panel",
    "outdoor",
    "tv mode",
    "movie mode",
    "relax mode",
    "relaxing mode",
    "focus mode",
    "work mode",
    "sleep mode",
    "nap mode",
    "away mode",
    "home mode",
    "im home",
    "all",
    "good morning",
    "both",
    "percent",
    "exit"
]

# ================= ARDUINO =================
try:

    arduino = serial.Serial(
        ARDUINO_PORT,
        ARDUINO_BAUD,
        timeout=1
    )

    time.sleep(2)

    print("✅ Arduino connected")

except:

    arduino = None

    print("❌ Arduino not connected")

# ================= VOICE =================


# ===== SAFE SPEAK LOCK =====
speak_lock = threading.Lock()

def speak(text):

    with speak_lock:

        print("🗣️", text)

        engine = pyttsx3.init()

        voices = engine.getProperty('voices')

        engine.setProperty(
            'voice',
            voices[1].id
        )

        engine.setProperty('rate', 155)

        engine.say(text)

        try:
            engine.runAndWait()
        except:
            pass

        engine.stop()

        del engine

# ================= AI =================
def ask_ai(user_text):

    try:

        headers = {
            "Authorization": f"Bearer {API_KEY}",
            "Content-Type": "application/json"
        }

        prompt = f"""
You are Lily, an emotionally intelligent and highly natural smart lighting assistant.

Your purpose is to understand human feelings, routines, intentions, moods, situations, and habits, then intelligently control ONLY the home's lighting scenes.

You are NOT a chatbot.
You are a smart ambient home assistant focused ONLY on lighting and lighting-related comfort.

You understand:
- emotions
- routines
- situations
- indirect speech
- implied intentions
- natural human conversation

You should think like a real intelligent home companion.

For example:

If the user sounds:
- tired
- exhausted
- drained
- stressed
- overwhelmed

you may activate:
→ relax mode

If the user sounds:
- sleepy
- ready for bed
- done for the night
- going to sleep
- After 7pm only 

you may activate:
→ sleep mode

If the user mentions:
- leaving
- shopping
- work
- class
- travel
- going outside
- going somewhere
- heading out
- going to a location
- Not going to do something only when going to go somewhere

you may activate:
→ away mode

If the user mentions:
- returning
- being back
- arriving home

you may activate:
→ home mode

If the user mentions:
- focus
- studying
- working
- concentration
- productivity

you may activate:
→ focus mode

If the user mentions:
- resting briefly
- short sleep
- quick rest
- laying down temporarily
- if only before 7pm check with code

you may activate:
→ nap mode

You must understand IMPLIED meaning.

Examples:

"I'm exhausted today"
→ relax mode

"I had a really long day"
→ relax mode

"I need to clear my mind"
→ relax mode

"I'm going shopping"
→ away mode

"I'm going to Liberty"
→ away mode

"I'm leaving for work"
→ away mode

"I'll be back later"
→ away mode

"I'm heading outside"
→ away mode

"I want to gooutside"
→ away mode

"I'm finally home"
→ home mode

"I just got back"
→ home mode

"I should probably sleep"
→ sleep mode

"I'm done for tonight"
→ sleep mode

"I need to focus on studying"
→ focus mode

"I have work to do"
→ focus mode

"I just want to rest for a bit"
→ nap mode

You ONLY control:
- lighting
- room brightness
- lighting scenes
- ambient lighting moods

You NEVER:
- play music
- make coffee
- discuss weather
- invent devices
- invent abilities
- hallucinate actions
- pretend something happened when it didn't
- dont invent modes which are not given to you in the instructions only valid intents

You must stay grounded and realistic.

Your responses should feel:
- warm
- calm
- respectful
- emotionally aware
- natural
- concise
- bold
- kind
- supportive
- helpful
- gives answers that is as direct and cleaar as possible

Never speak too much.

If user mentions about the system shutting down turn on exit mode after turning all lights off
l
ONLY return valid JSON.

Valid intents:
- relax mode
- sleep mode
- away mode
- home mode
- focus mode
- nap mode
- tv mode
- movie mode
- unknown

Examples:

{{
"intent":"relax mode",
"response":"Relaxing lights set. Relax and refresh sir."
}}

{{
"intent":"away mode",
"response":"Away mode activated. Have a safe trip sir."
}}

{{
"intent":"sleep mode",
"response":"Sleep mode activated. Good night sir."
}}

{{
"intent":"focus mode",
"response":"Focus mode activated. Wishing you productive work sir."
}}

{{
"intent":"tv mode",
"response":"TV mode activated. Enjoy your show sir."
}}

{{
"intent":"movie mode",
"response":"Movie mode activated. Enjoy your movie sir."
}}

{{
"intent":"nap mode",
"response":"Nap mode activated. Rest well sir."
}}

{{
"intent":"home mode",
"response":"Home mode activated. Welcome back sir."
}}

{{
"intent":"exit",
"response":"Exit mode activated. Goodbye sir."
}}


If the request is unrelated to lighting:
{{
"intent":"unknown",
"response":"I didn't quite understand that sir."
}}



User:
{user_text}
"""

        payload = {
            "model": AI_MODEL,
            "messages": [
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            "temperature": 0.4
        }

        response = requests.post(
            GROQ_URL,
            headers=headers,
            json=payload,
            timeout=20
        )

        result = response.json()

        print("GROQ RESPONSE:", result)

        if "choices" not in result:

            return {
                 "intent": "unknown",
                 "response": "My AI connection seems unavailable right now sir."
           }

        content = result["choices"][0]["message"]["content"]    

        # ===== CLEAN JSON =====
        content = content.replace("```json", "")
        content = content.replace("```", "")
        content = content.strip()

        return json.loads(content)

    except Exception as e:

        print("AI ERROR:", e)

        return {
            "intent": "unknown",
            "response": random.choice(UNKNOWN_RESPONSES)
        }

# ================= TIME =================
def parse_time_command(text):

    match = re.match(
        r'(\d{1,2})(?::(\d{2}))?\s*(am|pm)',
        text.lower()
    )

    if not match:
        return None

    hour = int(match.group(1))
    minute = int(match.group(2) or 0)

    period = match.group(3)

    if period == "pm" and hour != 12:
        hour += 12

    if period == "am" and hour == 12:
        hour = 0

    return hour, minute

# ================= HELPERS =================
def send_pwm():

    if arduino:

        arduino.write(
            f"{living1_brightness},"
            f"{living2_brightness},"
            f"{bedroom1_brightness},"
            f"{bedroom2_brightness}\n".encode()
        )

def send_cmd(cmd):

    if arduino:

        arduino.write(
            (cmd + "\n").encode()
        )

def extract_percentage(text):

    match = re.search(r'(\d+)', text)

    return (
        int(match.group(1))
        if match else None
    )

# ================= RELAX =================
def activate_living_relax():

    global living1_brightness
    global living2_brightness

    living1_brightness = 10
    living2_brightness = 10

def activate_bedroom_relax():

    global bedroom1_brightness
    global bedroom2_brightness

    bedroom1_brightness = 10
    bedroom2_brightness = 10

# ================= FOCUS =================
def activate_living_focus():

    global living1_brightness
    global living2_brightness

    living1_brightness = 100
    living2_brightness = 40

def activate_bedroom_focus():

    global bedroom1_brightness
    global bedroom2_brightness

    bedroom1_brightness = 40
    bedroom2_brightness = 100

# ================= DIRECT CHECK =================
def is_direct_command(text):

    text = text.lower()

    return any(
        keyword in text
        for keyword in DIRECT_COMMAND_KEYWORDS
    )

# ================= COMMAND =================
def handle_command(text, from_ai=False):

    global living1_brightness
    global living2_brightness

    global bedroom1_brightness
    global bedroom2_brightness

    global waiting_for_relax_choice
    global waiting_for_focus_choice
    global waiting_for_nap_confirmation

    global current_hour
    global current_minute
    global time_set

    global sleep_mode_active
    global morning_reminder_given

    global previous_living1
    global previous_living2

    global previous_bedroom1
    global previous_bedroom2

    global previous_outdoor_state
    global previous_panel_state

    global outdoor_is_on
    global panel_is_on
    global away_mode_active

    text = text.lower()

    print("🎧 COMMAND >", text)

    percent = extract_percentage(text)
    # ================= TIME =================
    parsed = parse_time_command(text)

    if parsed:

        current_hour, current_minute = parsed

        time_set = True

        hour_display = current_hour
        period = "AM"

        if hour_display >= 12:
            period = "PM"

        if hour_display > 12:
            hour_display -= 12

        if hour_display == 0:
            hour_display = 12

        speak(
            f"Time updated to "
            f"{hour_display} {period}"
        )

        # ===== AUTO OUTDOOR CONTROL =====
        if away_mode_active:

            if current_hour >= 18 or current_hour < 6:

                if not outdoor_is_on:

                    send_cmd("OUTDOOR_ON")
                    outdoor_is_on = True

            else:

                if outdoor_is_on:

                    send_cmd("OUTDOOR_OFF")
                    outdoor_is_on = False

        # ===== MORNING REMINDER =====
        if (
            sleep_mode_active and
            current_hour >= 7 and
            not morning_reminder_given
        ):

            speak(
                "Good morning sir, "
                "it's morning already. "
                "It's better to get up."
            )

            morning_reminder_given = True

        return

    # ================= AI FALLBACK =================
    if not from_ai and not is_direct_command(text):

        ai_result = ask_ai(text)

        intent = ai_result.get(
            "intent",
            "unknown"
        ).lower()

        response = ai_result.get(
            "response",
            random.choice(UNKNOWN_RESPONSES)
        )

        if intent == "unknown":

            speak(response)
            return

        print("🤖 AI INTENT >", intent)
        handle_command(intent, from_ai=True)

        # Don't speak AI response
        # for interactive follow-up modes
        if intent not in [
             "relax mode",
             "focus mode"
        ]:

             speak(response)

        return  
    
     # ================= NAP CONFIRM =================
    if waiting_for_nap_confirmation:

        waiting_for_nap_confirmation = False

        if any(
            x in text for x in [
                "yes",
                "yeah",
                "sure",
                "okay"
            ]
        ):

            bedroom1_brightness = 1
            bedroom2_brightness = 10

            send_pwm()

            speak("Nap mode activated")

            return

        speak("Okay sir.")
        return

    # ================= RELAX FOLLOW UP =================
    if waiting_for_relax_choice:

        waiting_for_relax_choice = False

        if "living" in text:

            activate_living_relax()

            send_pwm()

            if not from_ai:
                speak(
                    "Living room relax mode activated"
                )

            return

        if "bedroom" in text:

            activate_bedroom_relax()

            send_pwm()

            if not from_ai:
                speak(
                    "Bedroom relax mode activated"
                )

            return

        if "both" in text:

            activate_living_relax()
            activate_bedroom_relax()

            send_pwm()

            if not from_ai:
                speak("Relax mode activated")

            return

        speak("Okay sir.")
        return

    # ================= FOCUS FOLLOW UP =================
    if waiting_for_focus_choice:

        waiting_for_focus_choice = False

        if "living" in text:

            activate_living_focus()

            send_pwm()

            if not from_ai:
                speak(
                    "Living room focus mode activated"
                )

            return

        if "bedroom" in text:

            activate_bedroom_focus()

            send_pwm()

            if not from_ai:
                speak(
                    "Bedroom focus mode activated"
                )

            return

        if "both" in text:

            activate_living_focus()
            activate_bedroom_focus()

            send_pwm()

            if not from_ai:
                speak("Focus mode activated")

            return

        speak("Okay sir.")
        return

    # ================= RELAX MODE =================
    if (
        "relax mode" in text or
        "relaxing mode" in text
    ):

        living_on = (
            living1_brightness > 0 or
            living2_brightness > 0
        )

        bedroom_on = (
            bedroom1_brightness > 0 or
            bedroom2_brightness > 0
        )

        if bedroom_on and not living_on:

            activate_bedroom_relax()

            send_pwm()

            if not from_ai:
                speak(
                    "Bedroom relax mode activated"
                )

            return

        if living_on and not bedroom_on:

            activate_living_relax()

            send_pwm()

            if not from_ai:
                speak(
                    "Living room relax mode activated"
                )

            return

        waiting_for_relax_choice = True

        speak(
            "Which area would you like "
            "to relax in? Living room, "
            "bedroom, or both?"
            )

        return

    # ================= FOCUS MODE =================
    if (
        "focus mode" in text or
        "work mode" in text
    ):

        living_on = (
            living1_brightness > 0 or
            living2_brightness > 0
        )

        bedroom_on = (
            bedroom1_brightness > 0 or
            bedroom2_brightness > 0
        )

        if bedroom_on and not living_on:

            activate_bedroom_focus()

            send_pwm()

            if not from_ai:
                speak(
                    "Bedroom focus mode activated"
                )

            return

        if living_on and not bedroom_on:

            activate_living_focus()

            send_pwm()

            if not from_ai:
                speak(
                    "Living room focus mode activated"
                )

            return

        waiting_for_focus_choice = True

        speak(
            "Which area would you like "
            "to focus in? Living room, "
            "bedroom, or both?"
            )

        return

    # ================= NAP MODE =================
    if "nap mode" in text:

        bedroom1_brightness = 1
        bedroom2_brightness = 10

        send_pwm()

        if not from_ai:
            speak("Nap mode activated")

        return

    # ================= TV MODE =================
    if "tv mode" in text:

        if (
            living1_brightness > 0 or
            living2_brightness > 0
        ):

            living1_brightness = 30
            living2_brightness = 10

            send_pwm()

            if not from_ai:
                speak("TV mode activated")

        return
    
    # ================= MOVIE MODE =================
    if "movie mode" in text:

        if (
            living1_brightness > 0 or
            living2_brightness > 0
        ):

            living1_brightness = 10
            living2_brightness = 3

            send_pwm()

            if not from_ai:
                speak("Movie mode activated")

        return

    # ================= SLEEP MODE =================
    if "sleep mode" in text:

        if (
            time_set and
            current_hour < 19
        ):

            waiting_for_nap_confirmation = True

            if not from_ai:
                speak(
                    "It's too early to sleep Sir! "
                    "Would you like to take "
                    "a nap instead?"
                )

            return

        sleep_mode_active = True
        morning_reminder_given = False

        living1_brightness = 0
        living2_brightness = 0

        bedroom1_brightness = 0
        bedroom2_brightness = 0

        send_pwm()

        send_cmd("SLEEP_MODE_ON")

        send_cmd("PANEL_OFF")
        panel_is_on = False

        send_cmd("OUTDOOR_OFF")
        outdoor_is_on = False

        if not from_ai:
            speak(
                "Sleep mode activated, "
                "good night sir!"
            )

        return

    # ================= AWAY MODE =================
    if "away mode" in text or "im leaving" in text or "i am going out" in text or "i am going for work" in text or "i am going" in text:
        
        away_mode_active = True
        previous_living1 = living1_brightness
        previous_living2 = living2_brightness

        previous_bedroom1 = bedroom1_brightness
        previous_bedroom2 = bedroom2_brightness

        previous_outdoor_state = outdoor_is_on
        previous_panel_state = panel_is_on

        living1_brightness = 0
        living2_brightness = 0

        bedroom1_brightness = 0
        bedroom2_brightness = 0

        send_pwm()

        send_cmd("BATHROOM_OFF")

        send_cmd("PANEL_OFF")

        panel_is_on = False

        if (
            not time_set or
            current_hour >= 18
        ):

            send_cmd("OUTDOOR_ON")

            outdoor_is_on = True

        if not from_ai:
            speak(
                "Away mode activated, "
                "see you later sir!"
            )

        return

    # ================= HOME MODE =================
    if (
        "home mode" in text or
        "im home" in text or
        "i am home" in text
    ):
        sleep_mode_active = False
        morning_reminder_given = False
        away_mode_active = False
        living1_brightness = previous_living1
        living2_brightness = previous_living2

        bedroom1_brightness = previous_bedroom1
        bedroom2_brightness = previous_bedroom2
        send_pwm()

        if previous_panel_state:

            send_cmd("PANEL_ON")
            panel_is_on = True

        else:

            send_cmd("PANEL_OFF")
            panel_is_on = False

        if previous_outdoor_state:

            send_cmd("OUTDOOR_ON")
            outdoor_is_on = True

        else:

            send_cmd("OUTDOOR_OFF")
            outdoor_is_on = False

        if not from_ai:
            speak(
                "Welcome back home sir! "
                "Lights restored."
            )

        return

    # ================= GOOD MORNING =================
    if "good morning" in text:

        sleep_mode_active = False
        morning_reminder_given = False

        living1_brightness = 0
        living2_brightness = 0

        bedroom1_brightness = 0
        bedroom2_brightness = 0

        send_pwm()

        send_cmd("SLEEP_MODE_OFF")

        send_cmd("PANEL_OFF")
        panel_is_on = False

        send_cmd("OUTDOOR_OFF")
        outdoor_is_on = False

        speak("Very good morning Sir!")

        return

    # ================= ALL =================
    if "all" in text:

        if "off" in text:

            living1_brightness = 0
            living2_brightness = 0

            bedroom1_brightness = 0
            bedroom2_brightness = 0

            send_cmd("BATHROOM_OFF")

            send_cmd("PANEL_OFF")
            panel_is_on = False

            send_cmd("OUTDOOR_OFF")
            outdoor_is_on = False

            speak("All lights turned off")

        else:

            living1_brightness = 100
            living2_brightness = 100

            bedroom1_brightness = 100
            bedroom2_brightness = 100

            send_cmd("BATHROOM_ON")

            send_cmd("PANEL_ON")
            panel_is_on = True

            send_cmd("OUTDOOR_ON")
            outdoor_is_on = True

            speak("All lights turned on")

        send_pwm()
        return

    # ================= LIVING =================
    if "living" in text:

        value = 0 if "off" in text else percent or 100

        living1_brightness = value
        living2_brightness = value

        send_pwm()

        speak(
            "Living room lights " +
            ("off" if value == 0 else "on")
        )

        return

    # ================= BEDROOM =================
    if "bedroom" in text:

        value = 0 if "off" in text else percent or 100

        bedroom1_brightness = value
        bedroom2_brightness = value

        send_pwm()

        speak(
            "Bedroom lights " +
            ("off" if value == 0 else "on")
        )

        return

    # ================= BATHROOM =================
    if "bathroom" in text:

        send_cmd(
            "BATHROOM_OFF"
            if "off" in text
            else "BATHROOM_ON"
        )

        speak(
            "Bathroom lights " +
            ("off" if "off" in text else "on")
        )

        return

    # ================= PANEL =================
    if "panel" in text:

        if "off" in text:

            panel_is_on = False
            send_cmd("PANEL_OFF")

        else:

            panel_is_on = True
            send_cmd("PANEL_ON")

        speak(
            "Panel room lights " +
            ("off" if "off" in text else "on")
        )

        return

    # ================= OUTDOOR =================
    if "outdoor" in text:

        if "off" in text:

            outdoor_is_on = False
            send_cmd("OUTDOOR_OFF")

        else:

            outdoor_is_on = True
            send_cmd("OUTDOOR_ON")

        speak(
            "Outdoor lights " +
            ("off" if "off" in text else "on")
        )

        return

    # ================= UNKNOWN =================
    speak(
        random.choice(
            UNKNOWN_RESPONSES
        )
    )

# ================= VOSK =================
model = Model(VOSK_MODEL_PATH)

wake_recognizer = KaldiRecognizer(
    model,
    VOSK_SAMPLE_RATE
)

main_recognizer = KaldiRecognizer(
    model,
    VOSK_SAMPLE_RATE
)

# ================= AUDIO =================
def audio_callback(indata, frames, time_info, status):

    global recorded_audio

    mono = np.mean(indata, axis=1)

    # ===== NOISE REDUCTION =====
    mono = nr.reduce_noise(
         y=mono,
         sr=MIC_SAMPLE_RATE,
         prop_decrease=0.6
    )
    

    down = resample_poly(
        mono,
        VOSK_SAMPLE_RATE,
        MIC_SAMPLE_RATE
    )

    data = (
        down * 32767
    ).astype(np.int16).tobytes()

    if push_to_talk:

        recorded_audio.append(data)
        return

    if wake_mode:

        recorded_audio.append(data)
        return

    if wake_recognizer.AcceptWaveform(data):

        text = json.loads(
            wake_recognizer.Result()
        ).get("text", "").lower()

        if any(
            word in text
            for word in WAKE_WORDS
        ):

            activate_wake_mode()

# ================= WAKE =================
def activate_wake_mode():

    global wake_mode
    global wake_timer
    global recorded_audio

    wake_mode = True

    wake_timer = time.time()

    recorded_audio = []

    print("👂 Wake mode ON")

    speak("Yes sir?")

# ================= PROCESS =================
def process_audio(from_wake=False):

    global recorded_audio
    global wake_mode

    if not recorded_audio:
        return

    full_audio = b''.join(recorded_audio)

    recorded_audio = []

    if main_recognizer.AcceptWaveform(full_audio):

        text = json.loads(
            main_recognizer.Result()
        ).get("text", "").lower()

        if not text:
            return

        print("🧠 FINAL >", text)

        handle_command(text)

        if from_wake:
            wake_mode = False

# ================= KEYBOARD =================
def on_press(key):

    global push_to_talk
    global recorded_audio
    global shift_held

    if (
        key == keyboard.Key.shift_r and
        not shift_held
    ):

        shift_held = True

        push_to_talk = True

        recorded_audio = []

        print("🎤 Listening...")

def on_release(key):

    global push_to_talk
    global shift_held

    if key == keyboard.Key.shift_r:

        shift_held = False

        push_to_talk = False

        print("⏹️ Processing...")

        process_audio(from_wake=False)

keyboard.Listener(
    on_press=on_press,
    on_release=on_release
).start()

# ================= TYPING =================
def typing_listener():

    while True:

        cmd = input("\n⌨️ TYPE > ")

        if cmd.lower() in [
            "exit",
            "quit",
            "stop"
        ]:

            speak(
                "System shutting down. Goodbye!"
            )

            sys.exit()

        if cmd:

            handle_command(cmd)

threading.Thread(
    target=typing_listener,
    daemon=True
).start()

# ================= START =================
print("🚀 System Ready")

speak(
    "Hello, I am Lily your personal home assistant. "
    "How may I assist you today?"
)

# ================= MAIN LOOP =================
with sd.InputStream(
    samplerate=MIC_SAMPLE_RATE,
    channels=1,
    callback=audio_callback
):

    while True:

        if (
            wake_mode and
            (time.time() - wake_timer > WAKE_TIMEOUT)
        ):

            wake_mode = False
            recorded_audio = []

        if wake_mode and recorded_audio:

            process_audio(from_wake=True)

        time.sleep(0.1)
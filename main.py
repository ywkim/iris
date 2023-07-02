import json
import struct
import logging
import subprocess
import wave
from datetime import datetime

import openai
import pvporcupine
import speech_recognition as sr
from pvrecorder import PvRecorder

# Wake word detection
picovoice_access_key = os.getenv("PICOVOICE_PICOVOICE_ACCESS_KEY")

# ISO-639-1 format
LANGUAGE = "ko"

KEYWORD_PATH = "iris_ko_mac_v2_2_0.ppn"
MODEL_PATH = "porcupine_params_ko.pv"

# OpenAI ChatCompletion
GPT_MODEL = "gpt-3.5-turbo"
SYSTEM_PROMPT = '너의 이름은 "이리스"야.'
# Load your API key from an environment variable or secret management service
openai_api_key = os.getenv("OPENAI_OPENAI_API_KEY")

# Apple Voice
VOICE = "Yuna"

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

openai.openai_api_key = openai_api_key

keywords = ["picovoice"]
porcupine = pvporcupine.create(
    picovoice_access_key=picovoice_access_key,
    keyword_paths=[KEYWORD_PATH],
    model_path=MODEL_PATH,
)

audio_device_index = -1

recorder = PvRecorder(
    device_index=audio_device_index, frame_length=porcupine.frame_length
)
recorder.start()

print("Listening ... (press Ctrl+C to exit)")


def transcribe():
    with open("command.wav", "rb") as f:
        transcription = openai.Audio.transcribe("whisper-1", f, language=LANGUAGE)

        command_text = transcription.get("text")
        if not command_text:
            logging.error("Failed to transribe audio")
            return
        logging.info("Transcribed command text: %s", command_text)

        try:
            response = openai.ChatCompletion.create(
                model=GPT_MODEL,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": command_text},
                ],
            )

            response_message = response["choices"][0]["message"]
            print(response_message)

            response_content = response_message["content"]

            subprocess.run(["say", "-v", VOICE, response_content])

        except openai.error.ServiceUnavailableError:
            pass


try:
    # Initialize the recognizer
    r = sr.Recognizer()

    # Adjust the noise level
    with sr.Microphone() as source:
        print("Adjusting for noise...")
        r.adjust_for_ambient_noise(source)
        print("Done")

    while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)

        if result >= 0:
            print("[%s] Detected %s" % (str(datetime.now()), keywords[result]))

            import speech_recognition as sr

            # Open the microphone as a source
            with sr.Microphone() as source:
                # Listen for a voice command until it ends
                print("Listening...")
                audio = r.listen(source, timeout=5, phrase_time_limit=10)
                print("Finished listening")

            # 오디오를 WAV 파일로 저장
            with open("command.wav", "wb") as out:
                out.write(audio.get_wav_data())

            transcribe()
        else:
            print("Not detected")

except KeyboardInterrupt:
    print("Stopping ...")
finally:
    recorder.delete()
    porcupine.delete()
    # if wav_file is not None:
    #     wav_file.close()

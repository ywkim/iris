import json
import struct
import subprocess
import wave
from datetime import datetime

import openai
import pvporcupine
from pvrecorder import PvRecorder

access_key = "YOUR_ACCESS_KEY"

# ISO-639-1 format
LANGUAGE = "ko"

KEYWORD_PATH = "iris_ko_mac_v2_2_0.ppn"
MODEL_PATH = "porcupine_params_ko.pv"

# Load your API key from an environment variable or secret management service
# api_key = os.getenv("OPENAI_API_KEY")
api_key = "YOUR_API_KEY"

# OpenAI ChatCompletion params
GPT_MODEL = "gpt-3.5-turbo"
SYSTEM_PROMPT = '너의 이름은 "이리스"야.'

# Apple Voice
VOICE = "Yuna"

openai.api_key = api_key

keywords = ["picovoice"]
porcupine = pvporcupine.create(
    access_key=access_key,
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
    output_path = "command.wav"
    wav_file = wave.open(output_path, "w")
    wav_file.setnchannels(1)
    wav_file.setsampwidth(2)
    wav_file.setframerate(16000)

    for _ in range(
        int(3 * porcupine.sample_rate / porcupine.frame_length)
    ):  # 3 seconds
        command_pcm = recorder.read()
        wav_file.writeframes(struct.pack("h" * len(command_pcm), *command_pcm))

    wav_file.close()

    with open("command.wav", "rb") as f:
        transcription = openai.Audio.transcribe("whisper-1", f, language=LANGUAGE)

        print(json.dumps(transcription, ensure_ascii=False))

        command_text = transcription["text"]
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
    while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)

        if result >= 0:
            print("[%s] Detected %s" % (str(datetime.now()), keywords[result]))

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

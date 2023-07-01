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

def listen():
    import webrtcvad
    import pyaudio
    import collections
    import struct
    import wave

    # Set sample rate and frame duration
    SAMPLE_RATE = 16000
    N_CHANNELS = 1
    SAMPLE_WIDTH = 2  # 16 bit
    CHUNK_DURATION_MS = 30  # 10, 20 or 30
    CHUNK_SIZE = int(SAMPLE_RATE * CHUNK_DURATION_MS / 1000)  # chunk to read
    PADDING_DURATION_MS = 1000  # chunk to read
    PADDING_SIZE = int(SAMPLE_RATE * PADDING_DURATION_MS / 1000)  # chunk to read

    # Create a VAD object
    vad = webrtcvad.Vad()

    # Set aggressiveness mode, which is a integer between 0 and 3. 0 is the least aggressive about filtering out non-speech, 3 is the most aggressive.
    vad.set_mode(3)

    # Initialize the microphone
    pa = pyaudio.PyAudio()
    sample_format = pa.get_format_from_width(SAMPLE_WIDTH)
    audio_stream = pa.open(
        format=sample_format,
        rate=SAMPLE_RATE,
        channels=N_CHANNELS,
        input=True,
        frames_per_buffer=CHUNK_SIZE)

    # Create a wave file to store the audio
    output_path = "command.wav"
    wav_file = wave.open(output_path, "wb")
    wav_file.setnchannels(N_CHANNELS)
    wav_file.setsampwidth(pa.get_sample_size(sample_format))
    wav_file.setframerate(SAMPLE_RATE)

    # Read audio until voice command ends
    while True:
        # Read a chunk of raw audio data from the microphone
        pcm = audio_stream.read(CHUNK_SIZE)

        # Convert raw data to int16 array
        # n_samples_per_buffer = n_frames_per_buffer * N_CHANNELS
        # in_data = struct.unpack("%dh" % n_samples_per_buffer, chunk)
        # pcm = struct.unpack_from("h" * 1024, pcm)

        # Use VAD to check if the current chunk contains speech
        is_speech = vad.is_speech(pcm, SAMPLE_RATE)

        # If the audio data contains speech, write it to the wave file
        if is_speech:
            print("Voice detected, start recording")
            wav_file.writeframes(pcm)

            # If speech is detected, continue reading audio chunks
            # until no speech is detected
            while True:
                is_speech = False
                for _ in range(PADDING_SIZE // CHUNK_SIZE):
                    pcm = audio_stream.read(CHUNK_SIZE)
                    wav_file.writeframes(pcm)
                    if vad.is_speech(pcm, SAMPLE_RATE):
                        print("Speech detected")
                        is_speech = True
                    else:
                        print("Speech not detected")
                if not is_speech:
                    print("Speech ended")
                    break
            break
        else:
            print("No speech detected")

    # Stop the recording
    audio_stream.stop_stream()
    audio_stream.close()
    pa.terminate()
    wav_file.close()

    transcribe()


try:
    while True:
        pcm = recorder.read()
        result = porcupine.process(pcm)

        if result >= 0:
            print("[%s] Detected %s" % (str(datetime.now()), keywords[result]))

            listen()
        else:
            print("Not detected")

except KeyboardInterrupt:
    print("Stopping ...")
finally:
    recorder.delete()
    porcupine.delete()
    # if wav_file is not None:
    #     wav_file.close()

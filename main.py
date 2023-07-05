from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage
from langchain.agents import AgentType, initialize_agent, load_tools

import configparser
import json
import logging
import os
import tempfile
import time
from datetime import datetime

import openai
import pvporcupine
import pyttsx4
import speech_recognition as sr
from pvrecorder import PvRecorder

DEFAULT_KEYWORD = "jarvis"

DEFAULT_CONFIG = {
    "paths": {
        "keyword_path": pvporcupine.KEYWORD_PATHS[DEFAULT_KEYWORD],
    },
    "settings": {
        "chat_model": "gpt-3.5-turbo",
        "system_prompt": "You are a helpful assistant.",
        "temperature": 0.7,
    },
}

logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(levelname)s - %(message)s"
)


class PorcupineWakeWordListener:
    def __init__(self, access_key, keyword_paths, model_path):
        self.porcupine = pvporcupine.create(
            access_key=access_key, keyword_paths=keyword_paths, model_path=model_path
        )
        audio_device_index = -1
        self.recorder = PvRecorder(
            device_index=audio_device_index, frame_length=self.porcupine.frame_length
        )

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def listen(self):
        try:
            self.recorder.start()
            logging.info("Listening wake word ...")

            while True:
                pcm = self.recorder.read()
                keyword_idx = self.porcupine.process(pcm)

                if keyword_idx >= 0:
                    logging.info(f"[{datetime.now()}] Detected keyword")
                    return keyword_idx

                else:
                    logging.debug("Not detected")
        finally:
            self.recorder.stop()

    def close(self):
        self.recorder.delete()
        self.porcupine.delete()


class SpeechSynthesizer:
    def __init__(self, voice=None):
        self.engine = pyttsx4.init()
        if voice:
            self.engine.setProperty("voice", voice)

    def speak(self, text):
        self.engine.say(text)
        # If we use runAndWait, there is an issue that the program terminates
        # abnormally.
        self.engine.startLoop(False)
        self.engine.iterate()
        while self.engine.isBusy():
            time.sleep(0.1)
        self.engine.endLoop()


class WhisperTranscriber:
    def __init__(self, language):
        # language: ISO-639-1 format
        self.language = language

    def transcribe(self, audio_file_name):
        with open(audio_file_name, "rb") as f:
            transcription = openai.Audio.transcribe(
                "whisper-1", f, language=self.language
            )
            command_text = transcription.get("text")
            logging.info("Transcribed command text: %s", command_text)
            return command_text


class VoiceActivityDetector:
    def __init__(self):
        self.recognizer = sr.Recognizer()

        # Adjust the noise level
        with sr.Microphone() as source:
            logging.info("Adjusting for noise...")
            self.recognizer.adjust_for_ambient_noise(source)
            logging.info("Done")

    def listen(self, audio_file_name):
        # Listen for a voice command until it ends
        with sr.Microphone() as source:
            logging.info("Listening...")
            audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
            logging.info("Finished listening")

        # Save audio as WAV file
        with open(audio_file_name, "wb") as out:
            out.write(audio.get_wav_data())
        return audio_file_name


class Iris:
    def __init__(self, config, wake, vad, stt, chat, tts):
        self.config = config
        self.wake = wake
        self.vad = vad
        self.stt = stt
        self.chat = chat
        self.tts = tts

    def run(self):
        try:
            while True:
                self.wake.listen()
                with tempfile.NamedTemporaryFile(suffix=".wav") as temp_file:
                    self.vad.listen(temp_file.name)
                    command_text = self.stt.transcribe(temp_file.name)
                    if not command_text:
                        logging.error("Failed to transcribe audio")
                        continue
                    response_message = self.chat.run(command_text=command_text)
                    logging.info("Chat Response: %s", response_message)
                    self.tts.speak(response_message)

        except KeyboardInterrupt:
            logging.info("Stopping...")
        finally:
            self.wake.close()


if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read_dict(DEFAULT_CONFIG)
    config.read("config.ini")

    with PorcupineWakeWordListener(
        config.get("api", "picovoice_access_key"),
        [config.get("paths", "keyword_path")],
        config.get("paths", "wake_model_path", fallback=None),
    ) as wake:
        vad = VoiceActivityDetector()

        openai.api_key = config.get("api", "openai_api_key")

        stt = WhisperTranscriber(config.get("settings", "language", fallback=None))

        chat = ChatOpenAI(
            model_name=config.get("settings", "chat_model"),
            temperature=config.get("settings", "temperature"),
        )
        tools = load_tools(["serpapi"])
        template = config.get("settings", "system_prompt")
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = "{command_text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        agent = initialize_agent(tools, chat, agent=AgentType.CHAT_ZERO_SHOT_REACT_DESCRIPTION, verbose=True)

        tts = SpeechSynthesizer(config.get("settings", "voice", fallback=None))

        iris = Iris(config, wake, vad, stt, chain, tts)
        iris.run()

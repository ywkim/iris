# Iris: AI Voice Assistant

## Table of Contents
1. [Introduction](#introduction)
1. [Features](#features)
1. [LangChain Integration](#langchain-integration)
1. [Installation](#installation)
1. [Configuration](#configuration)
1. [Usage](#usage)
1. [Technology Stack](#technology-stack)
1. [Contribution Guide](#contribution-guide)
1. [Community](#community)
1. [References](#references)
1. [License](#license)
1. [Contact](#contact)

## Introduction

Welcome to Iris (pronounced as /ˈiɾis/ in Spanish, [listen here](iris.mp3)), an open-source AI voice assistant designed to make your life easier. Named after the Greek goddess of messages and communication, Iris is here to help you manage your digital world with just your voice.

In today's fast-paced world, having a conversation with an AI has become an essential skill. However, finding an AI that can understand and respond to you in a meaningful way can be challenging. That's where Iris comes in. Powered by GPT, Iris can understand your voice commands and respond to them in a conversational manner. Whether you want to ask a question, get some advice, or just chat, Iris is here to listen and respond.

But Iris is more than just a voice assistant. It's a platform for exploration and innovation. Built with open-source technologies, Iris is fully customizable and extensible. You can add new features, improve existing ones, or even build your own voice assistant from scratch. And with the support of our growing community, you're never alone in your journey.

Join us in redefining what a voice assistant can do. Let's make technology more accessible and intuitive for everyone.

## Features

Iris offers a range of features designed to make your interactions with AI more natural and intuitive. Here are some of the key features:

- **Voice Activation**: Iris is always ready to listen. Just say the wake word, and Iris will start listening for your command.

- **Speech Recognition**: Iris can understand your voice commands. Powered by OpenAI's Whisper ASR API, Iris can transcribe your speech into text with high accuracy.

- **Conversational AI**: Iris can understand and respond to your commands in a conversational manner. Thanks to the GPT model, Iris can provide meaningful and contextually relevant responses.

- **Text-to-Speech**: Iris can speak to you. Using the pyttsx4 library, Iris can convert text responses into speech, providing a more natural interaction.

- **Customizable and Extensible**: Iris is built with open-source technologies, making it fully customizable and extensible. You can add new features, improve existing ones, or even build your own voice assistant from scratch.

- **Community Support**: Join our growing community of developers and users. Whether you need help with a problem, want to share your ideas, or are looking to contribute to the project, our community is here to support you.

## LangChain Integration

Iris now incorporates [LangChain](https://python.langchain.com/), a powerful language model chaining library. LangChain enables chaining together multiple language models and tools, paving the way for more complex and powerful applications.

The integration of LangChain has significantly expanded Iris's capabilities. Iris can now generate responses using OpenAI's language models and utilize a variety of tools provided by LangChain. One of these tools is SerpAPI, a search engine results page service. With SerpAPI, Iris can pull in real-time data from the web, making it possible to answer questions about current events or any topic that requires up-to-date information. This is a significant step forward, as it allows Iris to provide answers that are not only based on pre-existing knowledge but also on the most recent information available on the web.

For more information on how to use LangChain and the tools it provides, please refer to the [official LangChain documentation](https://python.langchain.com/docs/get_started/quickstart) and the [tools documentation](https://python.langchain.com/docs/modules/agents/tools/).

## Installation

1. **Python**: Iris requires Python 3.8 or higher. If you don't have Python installed, you can download it from the [official website](https://www.python.org/downloads/).

2. **Poetry**: Iris uses Poetry for dependency management. If you don't have Poetry installed, you can install it by following the instructions on the [official website](https://python-poetry.org/docs/#installation).

3. **Dependencies**: Once you have Poetry installed, navigate to the project directory in your terminal and run the following command to install the project dependencies:

    ```bash
    poetry install
    ```

4. **Configuration**: Before you can run Iris, you need to configure it. See the [Configuration](#configuration) section for more details.

That's it! You've successfully installed and set up Iris on your machine. If you encounter any issues during the installation process, feel free to reach out to our community for help.

## Configuration

Configuration for Iris is done via a `config.ini` file. Here is an example of what your `config.ini` might look like:

```ini
[api]
openai_api_key = your_openai_api_key
picovoice_access_key = your_picovoice_access_key
serpapi_api_key = your_serpapi_api_key

[paths]
keyword_path = iris_ko_mac_v2_2_0.ppn
wake_model_path = porcupine_params_ko.pv

[settings]
language = ko
chat_model = gpt-3.5-turbo-16k
system_prompt = You are a helpful assistant.
tools = serpapi
voice = com.apple.voice.premium.ko-KR.Yuna
```

### Required Settings

1. **Access Keys**
    - **OpenAI API Key**: This key is required for the chat feature. You can get this key from the [OpenAI website](https://beta.openai.com/signup/). Specify this key in the `openai_api_key` setting under the `[api]` section.
    - **Picovoice Access Key**: This key is required for the wake word feature. You can get this key from the [Picovoice Console](https://console.picovoice.ai/). Specify this key in the `picovoice_access_key` setting under the `[api]` section.
    - **SerpAPI Key**: This key is required for the search feature. You can get this key from the [SerpAPI website](https://serpapi.com/). Specify this key in the `serpapi_api_key` setting under the `[api]` section.

### Optional Settings

1. **Wake Word File**: The wake word is the word that Iris listens for to start processing voice commands. By default, Iris uses the built-in "jarvis" wake word. If you want to use a different wake word, you can create a custom wake word using the [Picovoice Console](https://console.picovoice.ai/). You will need to download the `.ppn` file for your custom wake word and specify its path in the `keyword_path` setting under the `[paths]` section.

2. **Voice**: This setting allows you to change the voice used by the TTS. The default voice is the system default. You can change this to any voice installed on your system by specifying the voice in the `voice` setting under the `[settings]` section.

3. **System Prompt**: This setting allows you to customize the system prompt that is used in the chat feature. The default prompt is "You are a helpful assistant.". You can change this by specifying your custom prompt in the `system_prompt` setting under the `[settings]` section.

4. **Tools**: The `tools` setting under the `[settings]` section allows you to specify the tools that you want to use with LangChain. The tools should be specified as a comma-separated list. The available tools are listed in the [LangChain tools documentation](https://python.langchain.com/docs/modules/agents/tools/).

## Usage

Once you have completed the installation and configuration, you can start Iris by running the following command in your terminal:

```bash
poetry run python main.py
```

Iris will start listening for the wake word. When the wake word is detected, Iris will start recording your voice command. Speak your command clearly. Once you finish speaking, Iris will process your command and respond verbally.

You can stop Iris at any time by pressing `Ctrl+C` in the terminal.

## Technology Stack

- **Python**: Iris is written in Python, a powerful, flexible language that's great for AI and machine learning projects.

- **OpenAI's Whisper ASR API**: For speech-to-text transcription, Iris uses OpenAI's Whisper ASR API, which is trained on 680,000 hours of multilingual and multitask supervised data collected from the web.

- **OpenAI's GPT**: For generating responses to user commands, Iris uses OpenAI's GPT, a state-of-the-art language model.

- **Porcupine**: For wake word detection, Iris uses Porcupine, a highly-accurate and lightweight wake word detection engine.

- **SpeechRecognition**: For voice activity detection, Iris uses the SpeechRecognition library, which makes it easy to recognize speech in a variety of languages.

- **pyttsx4**: For text-to-speech synthesis, Iris uses pyttsx4, a text-to-speech conversion library in Python that works offline.

## Contribution Guide

Contributions to Iris are very welcome! Here are some ways you can contribute:

- **Bug Reports**: If you encounter any bugs or issues, please open an issue on GitHub describing the problem and providing steps to reproduce it.

- **Feature Requests**: If you have ideas for new features or improvements, feel free to open an issue on GitHub to discuss it. Please provide as much context as possible about why you think the feature would be useful.

- **Code Contributions**: If you'd like to contribute code to fix a bug or implement a new feature, please open a pull request. Make sure to follow the existing code style and include tests if applicable.

- **Documentation**: Improvements to the documentation, whether it's typo fixes, rewording, or new content, are always appreciated.

Before contributing, please make sure to read and follow our Code of Conduct and Contribution Guidelines.

## Community

We have a vibrant and growing community of users and contributors. If you have questions, want to share your experiences, or just want to say hi, please join us!

- **Discord**: We have a [Discord server](https://discord.gg/3cWK9Qmv) where you can chat with other users and contributors, ask questions, and get help.

- **GitHub Discussions**: We use [GitHub Discussions](https://github.com/ywkim/iris/discussions) for more structured conversations and Q&A. It's a great place to ask for help, share your ideas, or discuss your use cases.

Remember, our community is a welcoming and respectful place. Please make sure to read and follow our Code of Conduct.

## References

Here are some resources that were helpful during the development of Iris:

- [Picovoice Porcupine](https://picovoice.ai/products/porcupine/)
- [OpenAI API](https://platform.openai.com/docs/)
- [SpeechRecognition](https://pypi.org/project/SpeechRecognition/)
- [pyttsx4](https://github.com/Jiangshan00001/pyttsx4)

## License

Iris is licensed under the [MIT License](LICENSE).

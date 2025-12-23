import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv
from rich import print
from openai import OpenAI
load_dotenv()

# setup AzureOpenAI client
gpt_client =  OpenAI(
    api_key = os.getenv("OPENAI_API_KEY"),
    base_url = os.getenv("OPENAI_BASE_URL"),

)

# Configure for local Docker image
speech_config = speechsdk.SpeechConfig(host="ws://localhost:5505")
audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

speech_config.speech_synthesis_voice_name = 'en-US-JaneNeural'

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# Stream OpenAI response to Speech Synthesizer
completion = gpt_client.chat.completions.create(
    model=os.getenv("OPENAI_MODEL_ID"),
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "tell me about gen ai in 100 words"}
    ],
    stream=True
)

sentence_buffer = ""
for chunk in completion:
    if chunk.choices[0].delta.content:
        text_chunk = chunk.choices[0].delta.content
        print(text_chunk, end="", flush=True)
        sentence_buffer += text_chunk

        # Synthesize when we have a complete sentence
        if any(punct in text_chunk for punct in ['.', '!', '?', '\n']):
            if sentence_buffer.strip():
                print(f"\n[TTS] Synthesizing: {sentence_buffer.strip()[:50]}...")
                result = speech_synthesizer.speak_text_async(sentence_buffer.strip()).get()

                if result.reason == speechsdk.ResultReason.Canceled:
                    cancellation_details = result.cancellation_details
                    print(f"\n[ERROR] Synthesis canceled: {cancellation_details.reason}")
                    if cancellation_details.error_details:
                        print(f"[ERROR] Details: {cancellation_details.error_details}")

                sentence_buffer = ""

# Synthesize any remaining text
if sentence_buffer.strip():
    print(f"\n[TTS] Synthesizing final: {sentence_buffer.strip()[:50]}...")
    result = speech_synthesizer.speak_text_async(sentence_buffer.strip()).get()

print("\n[DONE] Streaming complete")

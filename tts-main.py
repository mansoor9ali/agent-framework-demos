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

full_text = ""
for chunk in completion:
    if chunk.choices[0].delta.content:
        text_chunk = chunk.choices[0].delta.content
        full_text += text_chunk
        print(text_chunk, end="", flush=True)

# Synthesize complete text
speech_synthesis_result = speech_synthesizer.speak_text_async(full_text).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("\nSpeech synthesized successfully")
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print(f"\nSpeech synthesis canceled: {cancellation_details.reason}")
    if cancellation_details.error_details:
        print(f"Error details: {cancellation_details.error_details}")

import os
import asyncio
import signal
from typing import Optional

from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk

from utils import create_gptoss120b_client


class AzureVoiceAgent:
    def __init__(self) -> None:
        load_dotenv()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.chat_agent = create_gptoss120b_client().create_agent(
            name="VoiceDemoAgent",
            instructions="You are a helpful voice assistant."
        )
        speech_key = os.getenv("AZURE_STT_SUBSCRIPTIONKEY")
        speech_region = os.getenv("AZURE_STT_REGION")
        if not speech_key or not speech_region:
            raise ValueError("Azure Speech credentials missing in environment")
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=speechsdk.SpeechConfig(subscription=speech_key, region=speech_region),
            audio_config=speechsdk.audio.AudioConfig(use_default_microphone=True)
        )
        tts_key = os.getenv("AZURE_TTS_SUBSCRIPTIONKEY", speech_key)
        tts_region = os.getenv("AZURE_TTS_REGION", speech_region)
        self.synthesizer = speechsdk.SpeechSynthesizer(
            speech_config=speechsdk.SpeechConfig(subscription=tts_key, region=tts_region)
        )

    async def ask_agent(self, text: str) -> str:
        response_parts = []
        async for chunk in self.chat_agent.run_stream(text):
            if chunk.text:
                response_parts.append(chunk.text)
        return "".join(response_parts) or "I'm not sure how to answer."

    def speak(self, text: str) -> None:
        result = self.synthesizer.speak_text_async(text).get()
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError(f"Speech synthesis failed: {result.reason}")

    async def listen_and_respond(self) -> None:
        print("🎙️  Say something (Ctrl+C to stop)...")
        stt_result = self.recognizer.recognize_once_async().get()
        if stt_result.reason != speechsdk.ResultReason.RecognizedSpeech:
            print("🤔 Didn't catch that. Try again.")
            return
        user_text = stt_result.text.strip()
        if not user_text:
            print("🕳️ Detected silence.")
            return
        print(f"You said: {user_text}")
        agent_reply = await self.ask_agent(user_text)
        print(f"Agent: {agent_reply}")
        self.speak(agent_reply)

    def run(self) -> None:
        stop_event = asyncio.Event()

        def handle_stop(*_: Optional[int]) -> None:
            stop_event.set()

        signal.signal(signal.SIGINT, handle_stop)
        signal.signal(signal.SIGTERM, handle_stop)

        async def loop_body() -> None:
            while not stop_event.is_set():
                await self.listen_and_respond()

        self.loop.run_until_complete(loop_body())


def main() -> None:
    AzureVoiceAgent().run()


if __name__ == "__main__":
    main()

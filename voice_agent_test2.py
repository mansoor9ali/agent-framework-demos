import os
import asyncio
import signal
from typing import Optional

from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk
from agent_framework.openai import OpenAIChatClient


class AzureVoiceAgent:
    def __init__(self) -> None:
        load_dotenv()
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.chat_agent = OpenAIChatClient(
            api_key=os.getenv("OPENAI_API_KEY"),
            base_url=os.getenv("OPENAI_BASE_URL"),
            model_id=os.getenv("OPENAI_MODEL_ID"),
        ).create_agent(
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
        if not tts_key or not tts_region:
            raise ValueError("Azure TTS credentials missing in environment")
        streaming_endpoint = f"wss://{tts_region}.tts.speech.microsoft.com/cognitiveservices/websocket/v2"
        self.tts_config = speechsdk.SpeechConfig(endpoint=streaming_endpoint, subscription=tts_key)
        self.tts_config.speech_synthesis_voice_name = os.getenv("AZURE_TTS_VOICE", "en-US-AvaMultilingualNeural")
        self.tts_config.set_property(
            speechsdk.PropertyId.SpeechSynthesis_FrameTimeoutInterval,
            "100000000",
        )
        self.tts_config.set_property(
            speechsdk.PropertyId.SpeechSynthesis_RtfTimeoutThreshold,
            "10",
        )
        self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.tts_config)
        self.synthesizer.synthesizing.connect(lambda _: print("[audio]", end=""))

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

    async def stream_agent_reply(self, prompt: str) -> None:
        print("Agent:", end=" ", flush=True)
        tts_request = speechsdk.SpeechSynthesisRequest(
            input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream
        )
        tts_task = self.synthesizer.speak_async(tts_request)
        emitted = False
        async for chunk in self.chat_agent.run_stream(prompt):
            chunk_text = getattr(chunk, "text", None)
            if chunk_text:
                emitted = True
                print(chunk_text, end="", flush=True)
                tts_request.input_stream.write(chunk_text)
        if not emitted:
            fallback = "I'm not sure how to answer that."
            print(fallback, end="", flush=True)
            tts_request.input_stream.write(fallback)
        tts_request.input_stream.close()
        result = await asyncio.to_thread(tts_task.get)
        if result.reason != speechsdk.ResultReason.SynthesizingAudioCompleted:
            raise RuntimeError(f"Speech synthesis failed: {result.reason}")
        print()

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
        await self.stream_agent_reply(user_text)

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

"""Voice input/output utilities for advanced voice agent system."""

from __future__ import annotations

import asyncio
import os
import signal
from typing import AsyncIterator, Awaitable, Callable, Optional

from dotenv import load_dotenv
import azure.cognitiveservices.speech as speechsdk


class VoiceIO:
    """Wrap Azure STT/TTS setup and streaming helpers."""

    def __init__(self) -> None:
        load_dotenv(override=True)
        # Create STT recognizer
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        speech_key = os.getenv("AZURE_STT_SUBSCRIPTIONKEY")
        speech_region = os.getenv("AZURE_STT_REGION")
        if not speech_key or not speech_region:
            raise ValueError("Azure Speech credentials missing in environment")
        self.recognizer = speechsdk.SpeechRecognizer(
            speech_config=speechsdk.SpeechConfig(subscription=speech_key, region=speech_region),
            audio_config=speechsdk.audio.AudioConfig(use_default_microphone=True),
        )
        tts_key = os.getenv("AZURE_TTS_SUBSCRIPTIONKEY", speech_key)
        tts_region = os.getenv("AZURE_TTS_REGION", speech_region)
        if not tts_key or not tts_region:
            raise ValueError("Azure TTS credentials missing in environment")
        streaming_endpoint = f"wss://{tts_region}.tts.speech.microsoft.com/cognitiveservices/websocket/v2"
        self.tts_config = speechsdk.SpeechConfig(endpoint=streaming_endpoint, subscription=tts_key)
        self.tts_config.speech_synthesis_voice_name = os.getenv("AZURE_TTS_VOICE", "en-US-AvaMultilingualNeural")
        self.tts_config.set_property(speechsdk.PropertyId.SpeechSynthesis_FrameTimeoutInterval, "100000000")
        self.tts_config.set_property(speechsdk.PropertyId.SpeechSynthesis_RtfTimeoutThreshold, "10")
        self.synthesizer = speechsdk.SpeechSynthesizer(speech_config=self.tts_config)
        self.synthesizer.synthesizing.connect(lambda _: print("[audio]", end=""))

    async def start(self) -> None:
        """Initialize resources (placeholder for future)."""
        return None

    async def shutdown(self) -> None:
        """Cleanup resources if needed."""
        return None

    async def stream_reply(self, prompt: str, responder: Callable[[str], AsyncIterator[object]]) -> None:
        print("Agent:", end=" ", flush=True)
        tts_request = speechsdk.SpeechSynthesisRequest(
            input_type=speechsdk.SpeechSynthesisRequestInputType.TextStream
        )
        tts_task = self.synthesizer.speak_async(tts_request)
        emitted = False
        async for chunk in responder(prompt):
            chunk_text = getattr(chunk, "text", None)
            if chunk_text is None and isinstance(chunk, str):
                chunk_text = chunk
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

    async def listen_once(self) -> Optional[str]:
        print("🎙️  Say something (Ctrl+C to stop)...")
        stt_result = self.recognizer.recognize_once_async().get()
        if stt_result.reason != speechsdk.ResultReason.RecognizedSpeech:
            print("🤔 Didn't catch that. Try again.")
            return None
        user_text = stt_result.text.strip()
        if not user_text:
            print("🕳️ Detected silence.")
            return None
        print(f"You said: {user_text}")
        return user_text


class AdvancedVoiceAgentSystem:
    """High-level voice loop hooking into coordinator callable."""

    def __init__(
        self,
        responder: Callable[[str], AsyncIterator[object]],
        before_loop: Optional[Callable[[], Awaitable[None]]] = None,
        after_loop: Optional[Callable[[], Awaitable[None]]] = None,
    ) -> None:
        self.voice = VoiceIO()
        self.loop = self.voice.loop
        self.responder = responder
        self.before_loop = before_loop
        self.after_loop = after_loop

    def run(self) -> None:
        stop_event = asyncio.Event()

        def handle_stop(*_: Optional[int]) -> None:
            stop_event.set()

        signal.signal(signal.SIGINT, handle_stop)
        signal.signal(signal.SIGTERM, handle_stop)

        async def loop_body() -> None:
            while not stop_event.is_set():
                user_input = await self.voice.listen_once()
                if not user_input:
                    continue
                await self.voice.stream_reply(user_input, self.responder)

        async def wrapped_loop() -> None:
            if self.before_loop:
                await self.before_loop()
            try:
                await loop_body()
            finally:
                if self.after_loop:
                    await self.after_loop()

        self.loop.run_until_complete(wrapped_loop())

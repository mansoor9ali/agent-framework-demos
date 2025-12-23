import os
import azure.cognitiveservices.speech as speechsdk
import json
from dotenv import load_dotenv
from rich import print
from rich.logging import RichHandler

load_dotenv()

# Creates an instance of a speech config with specified endpoint and subscription key.
# Replace with your own endpoint and subscription key in config file.
speech_key = os.getenv("AZURE_TTS_SUBSCRIPTIONKEY")
speech_endpoint = os.getenv("AZURE_TTS_ENDPOINT")
service_region = os.getenv("AZURE_TTS_REGION")
# This example requires environment variables named "SPEECH_KEY" and "ENDPOINT"
# Replace with your own subscription key and endpoint, the endpoint is like : "https://YourServiceRegion.api.cognitive.microsoft.com"
#speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)

speech_config = speechsdk.SpeechConfig( host="http://localhost:5505")

audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)

# The neural multilingual voice can speak different languages based on the input text.
speech_config.speech_synthesis_voice_name='en-US-AvaMultilingualNeural'
speech_config.speech_synthesis_voice_name='en-US-JaneNeural'

speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

# Get text from the console and synthesize to the default speaker.
print("Here is some text that you want to speak >")
text = "My name is Jane and i am a neural voice"

speech_synthesis_result = speech_synthesizer.speak_text_async(text).get()

if speech_synthesis_result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
    print("Speech synthesized for text [{}]".format(text))
elif speech_synthesis_result.reason == speechsdk.ResultReason.Canceled:
    cancellation_details = speech_synthesis_result.cancellation_details
    print("Speech synthesis canceled: {}".format(cancellation_details.reason))
    if cancellation_details.reason == speechsdk.CancellationReason.Error:
        if cancellation_details.error_details:
            print("Error details: {}".format(cancellation_details.error_details))
            print("Did you set the speech resource key and endpoint values?")


#
# '''
#   For more samples please visit https://github.com/Azure-Samples/cognitive-services-speech-sdk
# '''
#
# import azure.cognitiveservices.speech as speechsdk
#
# # Creates an instance of a speech config with specified subscription key and service region.
# speech_key = "76a4add21b1d479a9cc37d728c775443"
# service_region = "eastasia"
#
# speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=service_region)
# # Note: the voice setting will not overwrite the voice element in input SSML.
# speech_config.speech_synthesis_voice_name = "en-US-AvaMultilingualNeural"
#
# text = "Hi, this is Ava Multilingual"
#
# # use the default speaker as audio output.
# speech_synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config)
#
# result = speech_synthesizer.speak_text_async(text).get()
# # Check result
# if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
#     print("Speech synthesized for text [{}]".format(text))
# elif result.reason == speechsdk.ResultReason.Canceled:
#     cancellation_details = result.cancellation_details
#     print("Speech synthesis canceled: {}".format(cancellation_details.reason))
#     if cancellation_details.reason == speechsdk.CancellationReason.Error:
#         print("Error details: {}".format(cancellation_details.error_details))


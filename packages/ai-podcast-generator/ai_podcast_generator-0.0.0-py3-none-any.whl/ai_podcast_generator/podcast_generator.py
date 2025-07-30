import asyncio
import io
import pyaudio
import traceback
from pathlib import Path
from pydub import AudioSegment
from google import genai
from google.genai.types import Content, Part, GenerateContentConfig
from .prompts import get_host_prompt, get_guest_prompt, get_script_prompt
from .utils import parse_script, reset_audio_buffer, get_current_audio_duration, _global_audio_buffer

class PodcastGenerator:
    def __init__(self, api_key, language="english"):
        """Initialize the podcast generator with Gemini API key and language."""
        if language.lower() not in ["hindi", "marathi", "english"]:
            raise ValueError("Language must be 'hindi', 'marathi', or 'english'")
        self.language = language.lower()
        self.client = genai.Client(
            api_key=api_key,
            http_options={"api_version": "v1beta"},
        )
        self.pya = pyaudio.PyAudio()
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.SAMPLE_RATE = 24000
        self.CHUNK_SIZE = 1024
        self.MODEL_TTS = "models/gemini-2.0-flash-exp"
        self.VOICE_HOST = "Kore"
        self.VOICE_GUEST = "Charon"

    async def _speak(self, sentence, voice, prompt, output_path=None, reset_buffer=False):
        """Synthesize speech and either play or save it."""
        if reset_buffer:
            reset_audio_buffer()

        config = {
            "response_modalities": ["AUDIO"],
            "speechConfig": {
                "voiceConfig": {"prebuiltVoiceConfig": {"voiceName": voice}},
            },
            "system_instruction": Content(parts=[Part(text=prompt)]),
        }
        current_pcm_buffer = io.BytesIO()

        try:
            async with self.client.aio.live.connect(model=self.MODEL_TTS, config=config) as session:
                playback_stream = None
                if output_path is None:  # Play directly
                    playback_stream = self.pya.open(
                        format=self.FORMAT,
                        channels=self.CHANNELS,
                        rate=self.SAMPLE_RATE,
                        output=True,
                    )

                await session.send(input=sentence, end_of_turn=True)
                async for response in session.receive():
                    if response.data:
                        audio_chunk = response.data
                        current_pcm_buffer.write(audio_chunk)
                        if playback_stream:
                            playback_stream.write(audio_chunk)
                    if response.text:
                        print(response.text, end="")

                if playback_stream:
                    playback_stream.close()

            current_pcm_buffer.seek(0)
            current_audio = AudioSegment.from_raw(
                current_pcm_buffer,
                sample_width=2,
                frame_rate=self.SAMPLE_RATE,
                channels=self.CHANNELS
            )

            global _global_audio_buffer
            if _global_audio_buffer is None:
                _global_audio_buffer = current_audio
            else:
                _global_audio_buffer += current_audio

            if output_path:
                _global_audio_buffer.export(output_path, format="mp3")
                print(f"Saved to {output_path} (duration: {len(_global_audio_buffer)/1000:.2f}s)")

        except Exception as e:
            print("Error in _speak():", e)
            traceback.print_exc()

    def _generate_script(self, topic, num_rounds):
        """Generate podcast script using Gemini API."""
        model = "gemini-2.0-flash-lite"
        prompt = get_script_prompt(self.language, topic, num_rounds)
        contents = [Content(role="user", parts=[Part(text=prompt)])]
        config = GenerateContentConfig(response_mime_type="text/plain")
        print("Generating podcast script...")
        script_text = ""
        for chunk in self.client.models.generate_content_stream(
            model=model, contents=contents, config=config
        ):
            script_text += chunk.text
        return parse_script(script_text, num_rounds)

    def run_podcast(self, topic, num_rounds=2, output=True, output_path=None):
        """Run the podcast with the given topic and settings."""
        if output and output_path is None:
            output_path = f"{topic.replace(' ', '_')}_podcast.mp3"
        script = self._generate_script(topic, num_rounds)
        print(f"Generated script with {len(script)} rounds")

        async def _run():
            for i, (question, answer) in enumerate(script):
                print(f"\n--- Round {i+1} ---")
                reset_buffer = (i == 0)
                host_prompt = get_host_prompt(self.language)
                guest_prompt = get_guest_prompt(self.language)
                print(f"Host: {question}")
                await self._speak(
                    question, self.VOICE_HOST, host_prompt,
                    output_path if output else None, reset_buffer
                )
                print(f"Guest: {answer}")
                await self._speak(
                    answer, self.VOICE_GUEST, guest_prompt,
                    output_path if output else None, False
                )
                print(f"Completed round {i+1}, duration: {get_current_audio_duration():.2f}s")
            print(f"\nPodcast complete! Duration: {get_current_audio_duration():.2f}s")
            if output:
                print(f"Saved to: {output_path}")

        asyncio.run(_run())

    def __del__(self):
        """Clean up pyaudio resources."""
        self.pya.terminate()
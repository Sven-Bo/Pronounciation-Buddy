from elevenlabs.client import ElevenLabs
from io import BytesIO


# Initialize the ElevenLabs client
def initialize_elevenlabs(api_key):
    return ElevenLabs(api_key=api_key)


# Function to generate audio for a given text
def generate_audio(client, text):
    audio_generator = client.generate(
        text=text,
        voice="Alexander Kensington - Studio Quality",
        model="eleven_multilingual_v2",
    )
    audio_bytes = BytesIO(b"".join(audio_generator))
    return audio_bytes

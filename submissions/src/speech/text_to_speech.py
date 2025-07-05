from pyaudio import PyAudio, Stream
from tempfile import NamedTemporaryFile
from wave import open, Wave_read
from time import sleep
from groq import Groq
import os

class TTS:
    def __init__(self, client: Groq, model: str='playai-tts' , verbose=False):
        self.audio = PyAudio()
        self.client=client
        self.model=model
        self.audio_data: Wave_read = None
        self.stream = None
        self.chunk_size = 1024
        self.verbose = verbose
        self.tempfile_path = ''

    def load_audio(self, file_path: str):
        """Load the audio file for playback."""
        if self.audio_data:
            self.audio_data.close()  # Close previous file if open
        self.audio_data = open(file_path, 'rb')

    def setup_stream(self):
        """Initialize the audio stream."""
        if self.audio_data is None:
            self.audio=PyAudio()
        
        self.stream = self.audio.open(
            format=self.audio.get_format_from_width(self.audio_data.getsampwidth()),
            channels=self.audio_data.getnchannels(),
            rate=self.audio_data.getframerate(),
            output=True
        )
    
    def get_stream(self) -> Stream:
        """Retrieve the current audio stream, initializing if necessary."""
        if self.stream is None:
            self.setup_stream()
        return self.stream
    
    def generate_tempfile(self):
        """Create a temporary WAV file for generated audio."""
        temp_file = NamedTemporaryFile(delete=False, suffix='.wav')
        self.tempfile_path = temp_file.name
        temp_file.close()
    
    def play_audio(self):
        """Play the generated audio file."""
        # Ensure the stream is reset before playing
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None  # Reset stream

        # Reload the audio file since it was fully read before
        self.load_audio(self.tempfile_path)  

        # Initialize the stream again
        self.stream = self.get_stream()
        
        data = self.audio_data.readframes(self.chunk_size)
        if self.verbose:
            print("Playing audio...")

        while data:
            self.stream.write(data)
            data = self.audio_data.readframes(self.chunk_size)

        if self.verbose:
            print("Audio played...")

        self.close()
        sleep(1.25)
        
        if self.tempfile_path and os.path.exists(self.tempfile_path):
            os.remove(self.tempfile_path)

    def generate_audio(self, text: str):
        """Generate audio using the LLM model."""
        self.generate_tempfile()
        if self.verbose:
            print(f'Processing text using {self.model}...')
        binary_response=self.client.audio.speech.create(model=self.model,voice='Celeste-PlayAI',input=text,response_format='wav')
        binary_response.write_to_file(self.tempfile_path)

    def invoke(self, text: str):
        """Generate audio and play it synchronously."""
        self.generate_audio(text)
        self.load_audio(self.tempfile_path)
        self.play_audio()

    def close(self):
        """Cleanup resources."""
        if self.stream is not None:
            if self.stream.is_active():
                self.stream.stop_stream()
            self.stream.close()
            self.stream = None

        if self.audio_data is not None:
            self.audio_data.close()
            self.audio_data = None
            
        if self.audio is not None:
            self.audio.terminate()

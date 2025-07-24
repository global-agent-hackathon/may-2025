# Global variable to store the session and client
_session = None
_s3_client = None


async def save_audio_to_s3(
    audio: bytes,
    sample_rate: int,
    num_channels: int,
    bucket_name: str,
    s3_prefix: str = "audio_recordings/",
):
    """
    Asynchronously save audio data to an S3 bucket with lazy loading and client reuse.

    Args:
        audio: Raw audio bytes
        sample_rate: Audio sample rate in Hz
        num_channels: Number of audio channels
        bucket_name: Name of the S3 bucket
        s3_prefix: Prefix/folder in S3 bucket (default: "audio_recordings/")

    Returns:
        str: S3 URI of saved file or None if error
    """
    # Lazy imports - only imported when function is called
    import io
    import wave
    import datetime
    import aioboto3

    global _session, _s3_client

    if len(audio) <= 0:
        print("No audio data to save")
        return None

    try:
        # Generate unique filename with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        key = f"{s3_prefix}conversation_recording_{timestamp}.wav"

        # Create WAV file in memory
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wf:
            wf.setsampwidth(2)
            wf.setnchannels(num_channels)
            wf.setframerate(sample_rate)
            wf.writeframes(audio)

        # Rewind the buffer for upload
        buffer.seek(0)

        # Initialize session and client if they don't exist
        if _session is None:
            _session = aioboto3.Session()

        if _s3_client is None:
            _s3_client = await _session.client("s3").__aenter__()

        # Use existing client
        await _s3_client.upload_fileobj(buffer, bucket_name, key)

        s3_uri = f"s3://{bucket_name}/{key}"
        print(f"Audio saved to {s3_uri}")
        return s3_uri

    except Exception as e:
        print(f"Error saving audio to S3: {e}")
        return None

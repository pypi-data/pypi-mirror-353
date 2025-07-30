import asyncio  # noqa: D100
import io
import json
import wave
from pathlib import Path
from typing import List, Optional

import aiofiles
from dotenv import load_dotenv
from env_config import api_config
from gcloud.aio.storage import Storage
from loguru import logger
from pydub import AudioSegment

from pipecat.frames.frames import TranscriptionMessage, TranscriptionUpdateFrame
from pipecat.processors.transcript_processor import TranscriptProcessor, UserTranscriptProcessor

load_dotenv(override=True)

# Initialize GCS client
storage = None

BUCKET_NAME = api_config.S3_BUCKET_NAME  # reuse same bucket name
TRANSCRIPT_FOLDER = "call-transcripts"
RECORDING_FOLDER = "call-recordings"
LOCAL_STORAGE_DIR = Path("/tmp/call-recordings")

LOCAL_STORAGE_DIR.mkdir(parents=True, exist_ok=True)


class TranscriptHandler:
    """Handles real-time transcript processing and output."""

    def __init__(self, logger):
        self.messages: List[TranscriptionMessage] = []
        self.logger = logger

    async def on_transcript_update(
        self, processor: TranscriptProcessor, frame: TranscriptionUpdateFrame
    ):
        self.logger.debug(f"Received transcript update with {len(frame.messages)} new messages")
        for msg in frame.messages:
            self.messages.append(msg)


async def save_audio_to_file(
    audio_data: bytes, sample_rate: int, num_channels: int, call_id: str
) -> str:
    """Save raw audio to a local file for later conversion."""
    try:
        # Define the file paths
        raw_path = LOCAL_STORAGE_DIR / f"{call_id}.raw"
        metadata_path = LOCAL_STORAGE_DIR / f"{call_id}.meta"

        logger.debug(f"Saving {len(audio_data)} bytes of audio to {raw_path}")

        # Open in append mode to handle existing files
        async with aiofiles.open(raw_path, "ab") as f:
            await f.write(audio_data)

        # Store metadata in a separate file if it doesn't exist yet
        if not metadata_path.exists():
            metadata = {"sample_rate": sample_rate, "num_channels": num_channels}
            async with aiofiles.open(metadata_path, "w") as f:
                await f.write(json.dumps(metadata))

        return str(raw_path)
    except Exception as e:
        logger.error(f"Error saving audio to file: {e}")
        return None


async def save_to_gcs(
    data: bytes, content_type: str, file_extension: str, folder: str, call_id: str
) -> Optional[str]:
    """Upload binary data to GCS."""
    try:
        global storage
        if not storage:
            storage = Storage(service_file="creds.json")
        path = f"{folder}/{call_id}.{file_extension}"
        logger.info(f"Uploading {len(data)} bytes to GCS at {path}")
        await storage.upload(BUCKET_NAME, path, data, content_type=content_type)
        url = f"https://storage.googleapis.com/{BUCKET_NAME}/{path}"
        logger.info(f"Successfully uploaded to GCS: {url}")
        return url
    except Exception as e:
        logger.error(f"Error uploading to GCS: {e}")
        return None


async def upload_recording_to_gcs(call_id: str) -> Optional[str]:
    """Convert raw audio to mp3 and upload to GCS."""
    try:
        global storage
        if not storage:
            storage = Storage(service_file="creds.json")
        raw_path = LOCAL_STORAGE_DIR / f"{call_id}.raw"
        metadata_path = LOCAL_STORAGE_DIR / f"{call_id}.meta"
        # wait for files
        for attempt in range(6):
            if raw_path.exists() and metadata_path.exists():
                break
            await asyncio.sleep(min(5, attempt + 1))
        else:
            logger.error(f"Audio files for call {call_id} not found")
            return None

        async with aiofiles.open(metadata_path, "r") as f:
            meta = json.loads(await f.read())
        async with aiofiles.open(raw_path, "rb") as f:
            audio_data = await f.read()
        if not audio_data:
            logger.error(f"No audio data for {call_id}")
            return None

        # convert PCM to MP3
        with io.BytesIO() as wav_buf:
            with wave.open(wav_buf, "wb") as wf:
                wf.setsampwidth(2)
                wf.setnchannels(meta["num_channels"])
                wf.setframerate(meta["sample_rate"])
                wf.writeframes(audio_data)
            wav_buf.seek(0)
            audio = AudioSegment.from_wav(wav_buf)
            mp3_buf = io.BytesIO()
            audio.export(mp3_buf, format="mp3", bitrate="64k")
            mp3_buf.seek(0)
            mp3_bytes = mp3_buf.read()

        recording_url = await save_to_gcs(mp3_bytes, "audio/mpeg", "mp3", RECORDING_FOLDER, call_id)
        # cleanup
        try:
            raw_path.unlink()
            metadata_path.unlink()
        except Exception:
            pass
        return recording_url
    except Exception as e:
        logger.error(f"Error uploading recording: {e}", exc_info=True)
        return None


async def store_transcript(call_id: str, transcript: list, should_upload_recording=False) -> bool:
    """Store transcript JSON and optionally upload recording."""
    filtered = (
        transcript[1:] if transcript and transcript[0].get("role") == "system" else transcript
    )
    try:
        body = json.dumps(filtered, ensure_ascii=False).encode("utf-8")
        # upload transcript
        logger.info(f"Uploading transcript for call {call_id}")
        await save_to_gcs(body, "application/json", "json", TRANSCRIPT_FOLDER, call_id)
        logger.info("Transcript uploaded")
        if should_upload_recording:
            await upload_recording_to_gcs(call_id)
        return True
    except Exception as e:
        logger.error(f"Error storing transcript: {e}", exc_info=True)
        return False


async def get_transcript_text(call_id: str) -> Optional[list]:
    """Retrieve transcript JSON from GCS."""
    try:
        path = f"{TRANSCRIPT_FOLDER}/{call_id}.json"
        data = await storage.download(BUCKET_NAME, path)
        return json.loads(data.decode("utf-8"))
    except Exception as e:
        logger.error(f"Error fetching transcript: {e}")
        return None


def get_transcript_url(call_id: str) -> str:
    """Public URL for transcript."""
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{TRANSCRIPT_FOLDER}/{call_id}.json"


def get_recording_url(call_id: str) -> str:
    """Public URL for recording."""
    return f"https://storage.googleapis.com/{BUCKET_NAME}/{RECORDING_FOLDER}/{call_id}.mp3"

from __future__ import annotations

from pathlib import Path
from typing import Optional, Tuple, List
from openai import OpenAI
from pydub import AudioSegment
import io
import uuid

from app.config import OPENAI_API_KEY, TTS_VOICE, TTS_MODEL, AUDIO_DIR

# OpenAI TTS has a 4096 character limit per request
MAX_CHUNK_CHARS = 4000


def _split_text(text: str) -> List[str]:
    """Split text into chunks that fit within TTS API limits.

    Splits on paragraph boundaries first, then sentence boundaries if needed.
    """
    if len(text) <= MAX_CHUNK_CHARS:
        return [text]

    chunks = []
    current = ""

    paragraphs = text.split("\n\n")
    for para in paragraphs:
        if len(current) + len(para) + 2 <= MAX_CHUNK_CHARS:
            current = f"{current}\n\n{para}" if current else para
        else:
            if current:
                chunks.append(current)
            # If a single paragraph exceeds the limit, split by sentences
            if len(para) > MAX_CHUNK_CHARS:
                sentences = para.replace(". ", ".\n").split("\n")
                current = ""
                for sentence in sentences:
                    if len(current) + len(sentence) + 1 <= MAX_CHUNK_CHARS:
                        current = f"{current} {sentence}" if current else sentence
                    else:
                        if current:
                            chunks.append(current)
                        current = sentence
            else:
                current = para

    if current:
        chunks.append(current)

    return chunks


def generate_audio(text: str, voice: Optional[str] = None) -> Tuple[str, int]:
    """Generate an MP3 from text using OpenAI TTS.

    Returns (filename, duration_in_seconds).
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    voice = voice or TTS_VOICE
    chunks = _split_text(text)

    if len(chunks) == 1:
        response = client.audio.speech.create(
            model=TTS_MODEL,
            voice=voice,
            input=chunks[0],
            response_format="mp3",
        )
        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = AUDIO_DIR / filename
        response.stream_to_file(str(filepath))
    else:
        # Generate each chunk and concatenate
        combined = AudioSegment.empty()
        for chunk in chunks:
            response = client.audio.speech.create(
                model=TTS_MODEL,
                voice=voice,
                input=chunk,
                response_format="mp3",
            )
            audio_bytes = io.BytesIO(response.content)
            segment = AudioSegment.from_mp3(audio_bytes)
            combined += segment

        filename = f"{uuid.uuid4().hex}.mp3"
        filepath = AUDIO_DIR / filename
        combined.export(str(filepath), format="mp3")

    # Get duration
    audio = AudioSegment.from_mp3(str(filepath))
    duration = len(audio) // 1000

    return filename, duration

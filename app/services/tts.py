from __future__ import annotations

import asyncio
import uuid
import struct
from typing import Optional, Tuple

import edge_tts

from app.config import TTS_VOICE, AUDIO_DIR


def _get_mp3_duration(filepath: str) -> int:
    """Estimate MP3 duration in seconds by reading frame headers."""
    bitrate_table = {
        1: [0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, 0],
        2: [0, 8, 16, 24, 32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, 0],
    }
    sample_rate_table = {0: 44100, 1: 48000, 2: 32000}

    total_frames = 0
    total_samples = 0

    with open(filepath, "rb") as f:
        data = f.read()

    i = 0
    while i < len(data) - 4:
        # Look for frame sync (11 bits set)
        if data[i] == 0xFF and (data[i + 1] & 0xE0) == 0xE0:
            header = struct.unpack(">I", data[i : i + 4])[0]
            version = (header >> 19) & 3  # 3=v1, 2=v2
            layer = (header >> 17) & 3  # 1=layer3
            bitrate_idx = (header >> 12) & 0xF
            sample_idx = (header >> 10) & 3

            if version == 3 and layer == 1 and bitrate_idx > 0 and sample_idx in sample_rate_table:
                bitrate = bitrate_table[1][bitrate_idx] * 1000
                sample_rate = sample_rate_table[sample_idx]
                padding = (header >> 9) & 1
                frame_size = (1152 * bitrate) // (8 * sample_rate) + padding
                if frame_size > 0:
                    total_frames += 1
                    total_samples += 1152
                    i += frame_size
                    continue

            elif version == 2 and layer == 1 and bitrate_idx > 0 and sample_idx in sample_rate_table:
                bitrate = bitrate_table[2][bitrate_idx] * 1000
                sample_rate = sample_rate_table[sample_idx]
                padding = (header >> 9) & 1
                frame_size = (576 * bitrate) // (8 * sample_rate) + padding
                if frame_size > 0:
                    total_frames += 1
                    total_samples += 576
                    i += frame_size
                    continue

        i += 1

    if total_frames > 0 and sample_idx in sample_rate_table:
        return total_samples // sample_rate_table[sample_idx]

    # Fallback: estimate from file size (assume 48kbps for edge-tts)
    import os
    file_size = os.path.getsize(filepath)
    return file_size // (48000 // 8)


async def _generate(text: str, voice: str, filepath: str) -> None:
    """Run edge-tts to generate an MP3 file."""
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(filepath)


def generate_audio(text: str, voice: Optional[str] = None) -> Tuple[str, int]:
    """Generate an MP3 from text using Edge TTS.

    Returns (filename, duration_in_seconds).
    """
    voice = voice or TTS_VOICE
    filename = "{}.mp3".format(uuid.uuid4().hex)
    filepath = str(AUDIO_DIR / filename)

    # edge-tts is async, so run it in an event loop
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                pool.submit(asyncio.run, _generate(text, voice, filepath)).result()
        else:
            loop.run_until_complete(_generate(text, voice, filepath))
    except RuntimeError:
        asyncio.run(_generate(text, voice, filepath))

    duration = _get_mp3_duration(filepath)
    return filename, duration

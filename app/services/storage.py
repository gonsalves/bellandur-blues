"""Audio file storage — Cloudflare R2 when configured, local filesystem otherwise."""

from __future__ import annotations

import os
import boto3
from app.config import (
    R2_ACCOUNT_ID,
    R2_ACCESS_KEY_ID,
    R2_SECRET_ACCESS_KEY,
    R2_BUCKET_NAME,
    R2_PUBLIC_URL,
    AUDIO_DIR,
    BASE_URL,
)


def _r2_enabled() -> bool:
    return all([R2_ACCOUNT_ID, R2_ACCESS_KEY_ID, R2_SECRET_ACCESS_KEY, R2_BUCKET_NAME])


def _get_s3_client():
    return boto3.client(
        "s3",
        endpoint_url="https://{}.r2.cloudflarestorage.com".format(R2_ACCOUNT_ID),
        aws_access_key_id=R2_ACCESS_KEY_ID,
        aws_secret_access_key=R2_SECRET_ACCESS_KEY,
        region_name="auto",
    )


def upload_audio(local_path: str, filename: str) -> str:
    """Upload an audio file and return its public URL.

    Uses R2 if configured, otherwise keeps the file local.
    """
    if _r2_enabled():
        client = _get_s3_client()
        client.upload_file(
            local_path,
            R2_BUCKET_NAME,
            filename,
            ExtraArgs={"ContentType": "audio/mpeg"},
        )
        # Clean up local temp file
        os.remove(local_path)
        return get_audio_url(filename)

    # Local mode — file is already in AUDIO_DIR
    return "{}/audio/{}".format(BASE_URL, filename)


def get_audio_url(filename: str) -> str:
    """Return the public URL for an audio file."""
    if _r2_enabled() and R2_PUBLIC_URL:
        return "{}/{}".format(R2_PUBLIC_URL.rstrip("/"), filename)
    return "{}/audio/{}".format(BASE_URL, filename)


def delete_audio(filename: str) -> None:
    """Delete an audio file from storage."""
    if _r2_enabled():
        client = _get_s3_client()
        client.delete_object(Bucket=R2_BUCKET_NAME, Key=filename)
    else:
        filepath = AUDIO_DIR / filename
        if filepath.exists():
            filepath.unlink()

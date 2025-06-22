"""services/orkes.py
~~~~~~~~~~~~~~~~~~~~
Thin wrapper around the Orkes Conductor REST API.
Responsible for:
  • Getting authentication token
  • Triggering a workflow (start_workflow)
  • Polling workflow status / output (get_workflow_status)

All heavy lifting—summarising, translating, TTS, S3 upload—is done
INSIDE the Orkes workflow definition. This module is *only* a proxy.
"""
from __future__ import annotations

import logging
import base64
import io
from typing import Any, Dict
import json

import requests
from requests import HTTPError

from app.utils.config import settings  # Expects ORKES_KEY_ID and ORKES_KEY_SECRET

logger = logging.getLogger(__name__)

WORKFLOW_NAME = "claude_to_gemini_using_integration"  # Update if your workflow name differs
ORKES_BASE_URL = "https://developer.orkescloud.com"

def get_orkes_token() -> str:
    """Get authentication token from Orkes."""
    url = f"{ORKES_BASE_URL}/api/token"
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "keyId": settings.ORKES_KEY_ID,
        "keySecret": settings.ORKES_KEY_SECRET
    }
    
    try:
        resp = requests.post(url, headers=headers, json=data, timeout=30)
        resp.raise_for_status()
        token = resp.json()['token']
        logger.info("Successfully obtained Orkes token")
        return token
    except HTTPError as exc:
        logger.error("Failed to get Orkes token: %s", exc)
        raise RuntimeError("Failed to authenticate with Orkes") from exc


def start_workflow(*, repo_url: str, mode: str = "narration") -> str:
    """Kick off an Orkes workflow and return its workflow ID.

    Args:
        repo_url: GitHub repository URL.
        mode: Either "narration", "interview", etc. Passed through to the
              workflow's input parameters.

    Returns:
        workflow_id: The ID returned by Orkes, used to poll status later.
    """
    # Get authentication token
    token = get_orkes_token()
    
    url = f"{ORKES_BASE_URL}/api/workflow"
    headers = {
        "x-authorization": token,
        "Content-Type": "application/json"
    }
    
    payload = {
        "name": WORKFLOW_NAME,
        "version": 1,
        "input": {
            "repo_url": repo_url,
            "mode": mode,
        },
    }

    logger.debug("POST %s -> %s", url, payload)

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=30)
        resp.raise_for_status()
    except HTTPError as exc:
        logger.error("Orkes start workflow failed: %s", exc)
        raise RuntimeError("Failed to start workflow with Orkes") from exc

    workflow_id = resp.text.strip()
    if not workflow_id:
        logger.error("Unexpected Orkes response: %s", resp.text)
        raise RuntimeError("Invalid response from Orkes: missing workflowId")

    logger.info("Started workflow %s for repo %s", workflow_id, repo_url)
    return workflow_id


def get_workflow_status(workflow_id: str) -> Dict[str, Any]:
    """Fetch the current status (and output) of an Orkes workflow.

    Args:
        workflow_id: ID returned by :func:`start_workflow`.

    Returns:
        A dict containing the workflow status and any outputs provided by
        your workflow (e.g., base64 audio blob).
    """
    token = get_orkes_token()
    
    url = f"{ORKES_BASE_URL}/api/workflow/{workflow_id}?summarize=true"
    headers = {
        "x-authorization": token,
        "Content-Type": "application/json"
    }
    
    logger.debug("GET %s", url)

    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
    except HTTPError as exc:
        logger.error("Orkes status fetch failed: %s", exc)
        raise RuntimeError("Failed to fetch workflow status from Orkes") from exc

    data: Dict[str, Any] = resp.json()
    return data

# ------------------ CONFIGURABLE VOICES ------------------
def get_voice(index: int) -> str:
    return "brandon" if index % 2 == 0 else "elowen"

# ------------------ ASYNC LMNT REQUEST ------------------
async def fetch_tts(session: aiohttp.ClientSession, text: str, voice: str) -> bytes:
    payload = {
        "voice": voice,
        "text": text,
        "model": "blizzard",
        "language": "auto",
        "format": "mp3",
        "sample_rate": 24000,
        "seed": 123,
        "top_p": 0.8,
        "temperature": 1
    }
    headers = {"X-API-Key": LMNT_API_KEY}
    async with session.post(LMNT_API_URL, json=payload, headers=headers) as response:
        response.raise_for_status()
        return await response.read()

# ------------------ MAIN ASYNC LOGIC ------------------
async def process_conversation(conversation: List[str]) -> List[bytes]:
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_tts(session, text, get_voice(i)) for i, text in enumerate(conversation)]
        return await asyncio.gather(*tasks)

# ------------------ MERGE + UPLOAD ------------------
def merge_and_upload(audio_chunks: List[bytes]) -> str:
    merged = AudioSegment.empty()
    for chunk in audio_chunks:
        audio = AudioSegment.from_file(io.BytesIO(chunk), format="mp3")
        merged += audio

    buffer = io.BytesIO()
    merged.export(buffer, format="mp3")
    buffer.seek(0)

    s3 = boto3.client("s3")
    key = str(uuid.uuid4())
    s3.upload_fileobj(buffer, AWS_S3_BUCKET, key, ExtraArgs={"ContentType": "audio/mpeg"})
    return f"https://{AWS_S3_BUCKET}.s3.amazonaws.com/{key}"

# ------------------ ENTRY POINT ------------------
def get_audio_file(conversation: List[str]) -> str:
    """Run TTS on each text chunk, merge, upload to S3, and return the public URL."""
    try:
        audio_results = asyncio.run(process_conversation(conversation))
        return merge_and_upload(audio_results)
    except Exception as e:
        raise RuntimeError(f"Error generating audio: {e}")

# ------------------ S3-BASED EXTRACTOR ------------------
def extract_audio_via_s3(workflow_id: str) -> StreamingResponse:
    """
    Fetches the workflow summary, generates audio via LMNT, uploads to S3,
    and streams the MP3 bytes back.
    """
    data = get_workflow_status(workflow_id)
    print(json.dumps(data, indent=2))
    if data.get("status") != "COMPLETED":
        raise RuntimeError(f"Workflow not completed yet: {data.get('status')}")

    summary = data.get("output", {}).get("summary")
    if not isinstance(summary, list):
        raise RuntimeError("Workflow output missing 'summary' list")

    s3_url = get_audio_file(summary)
    resp = requests.get(s3_url, timeout=20)
    resp.raise_for_status()
    return StreamingResponse(io.BytesIO(resp.content), media_type="audio/mpeg")

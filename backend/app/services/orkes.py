"""services/orkes.py
~~~~~~~~~~~~~~~~~~~~
Thin wrapper around the Orkes Conductor REST API.
Responsible for:
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

import requests
from requests import HTTPError

from app.utils.config import settings  # Expects ORKES_BASE_URL and ORKES_API_KEY

logger = logging.getLogger(__name__)

WORKFLOW_NAME = "generate_git_podcast"  # Update if your workflow name differs
HEADERS = {
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Authorization": f"Bearer {settings.ORKES_API_KEY}",
}


def start_workflow(*, repo_url: str, mode: str = "narration") -> str:
    """Kick off an Orkes workflow and return its workflow ID.

    Args:
        repo_url: GitHub repository URL.
        mode: Either "narration", "interview", etc. Passed through to the
              workflow's input parameters.

    Returns:
        workflow_id: The ID returned by Orkes, used to poll status later.
    """
    payload: Dict[str, Any] = {
        "name": WORKFLOW_NAME,
        "input": {
            "repo_url": repo_url,
            "mode": mode,
        },
    }

    url = f"{settings.ORKES_BASE_URL}/workflow/{WORKFLOW_NAME}"
    logger.debug("POST %s -> %s", url, payload)

    try:
        resp = requests.post(url, json=payload, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except HTTPError as exc:
        logger.error("Orkes start workflow failed: %s", exc)
        raise RuntimeError("Failed to start workflow with Orkes") from exc

    data = resp.json()
    workflow_id = data.get("workflowId") or data.get("workflow_id")
    if not workflow_id:
        logger.error("Unexpected Orkes response: %s", data)
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
    url = f"{settings.ORKES_BASE_URL}/workflow/{workflow_id}"
    logger.debug("GET %s", url)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except HTTPError as exc:
        logger.error("Orkes status fetch failed: %s", exc)
        raise RuntimeError("Failed to fetch workflow status from Orkes") from exc

    data: Dict[str, Any] = resp.json()
    return data


def extract_audio_blob(workflow_id: str) -> bytes:
    """
    Fetches base64-encoded audio blob from Orkes workflow and decodes it to bytes.

    Args:
        workflow_id: The ID of the completed Orkes workflow.

    Returns:
        MP3 file content as raw bytes.
    """
    data = get_workflow_status(workflow_id)

    if data.get("status") != "COMPLETED":
        raise RuntimeError("Workflow is not completed yet.")

    audio_b64 = data.get("output", {}).get("audio_blob_base64")
    if not audio_b64:
        raise RuntimeError("Audio blob not found in workflow output.")

    return base64.b64decode(audio_b64)

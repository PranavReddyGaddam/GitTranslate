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
    try:
        resp = requests.get(url, headers=headers, timeout=20)
        resp.raise_for_status()
        try:
            data = resp.json()
        except Exception:
            data = {"raw_response": resp.text}
        return data
    except HTTPError as exc:
        raise RuntimeError(f"Failed to fetch workflow status from Orkes: {exc}")

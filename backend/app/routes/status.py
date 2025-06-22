from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.orkes import extract_audio_via_s3, get_workflow_status
import io

router = APIRouter()

@router.get("/status/{workflow_id}")
async def get_status(workflow_id: str):
    """
    Return audio stream (via S3) or current status.
    """
    try:
        data = get_workflow_status(workflow_id)
        if data.get("status") != "COMPLETED":
            return {"status": data["status"]}

        # always use the S3-based extractor
        return extract_audio_via_s3(workflow_id)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

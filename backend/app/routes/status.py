from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from app.services.orkes import extract_audio_blob, get_workflow_status
import io

router = APIRouter()

@router.get("/status/{workflow_id}")
async def get_status(workflow_id: str):
    """
    Return audio stream (if available) or current status.
    """
    try:
        """
        status_data = get_workflow_status(workflow_id)

        if status_data.get("status") != "COMPLETED":
            return {"status": status_data.get("status")}

        audio_bytes = extract_audio_blob(workflow_id)
        
        return StreamingResponse(io.BytesIO(audio_bytes), media_type="audio/mpeg")
        """
        return {workflow_id: "Working"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

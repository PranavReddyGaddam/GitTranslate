from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.orkes import start_workflow

router = APIRouter()

class GenerateRequest(BaseModel):
    repo_url: HttpUrl

class GenerateResponse(BaseModel):
    workflow_id: str

@router.post("/generate", response_model=GenerateResponse)
async def generate_podcast(req: GenerateRequest):
    """
    Start a GitTranslate podcast generation workflow in Orkes.
    Returns the workflow ID to be used for status polling.
    """
    try:
        # For testing purposes, return a mock workflow ID
        # TODO: Uncomment the actual workflow call when Orkes is configured
        # workflow_id = start_workflow(
        #     repo_url=str(req.repo_url),
        # )
        # return {"workflow_id": workflow_id}
        
        # Mock response for testing
        return {"workflow_id": "test-workflow-123"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

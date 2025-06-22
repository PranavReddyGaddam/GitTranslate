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
        print(f"🚀 Starting workflow for repo: {req.repo_url}")
        
        workflow_id = start_workflow(
            repo_url=str(req.repo_url),
        )
        
        print(f"✅ Workflow started successfully!")
        print(f"📋 Workflow ID: {workflow_id}")
        print(f"📊 Check status at: GET /api/status/{workflow_id}")
        print("-" * 50)
        
        return {"workflow_id": workflow_id}
    except Exception as e:
        print(f"❌ Failed to start workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

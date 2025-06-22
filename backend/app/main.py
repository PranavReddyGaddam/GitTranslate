"""GitTranslate FastAPI Gateway
--------------------------------
Thin gateway service that forwards requests to Orkes Conductor.
No business logic, storage, or DB. Simply triggers and polls
Orkes workflows and exposes public endpoints for the Next.js
frontend.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import route blueprints (routers)
from app.routes.generate import router as generate_router  # POST /generate
from app.routes.status import router as status_router      # GET /status/{id}


def create_app() -> FastAPI:
    """Factory function to create the FastAPI application."""
    app = FastAPI(
        title="GitTranslate API",
        version="0.1.0",
        description="Gateway API that triggers and monitors Orkes workflows for GitTranslate."
    )

    # CORS: allow frontend (e.g., Vercel) to call this API
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # TODO: tighten for production
        allow_credentials=False,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    @app.get("/")
    def read_root():
        return {"message": "Hello, world!"}

    # Register route modules
    app.include_router(generate_router, prefix="/api", tags=["Generate"])
    app.include_router(status_router,   prefix="/api", tags=["Status"])

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

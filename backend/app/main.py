from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core import settings
from app.api import generation_router, export_router, images_router

# Create FastAPI app
app = FastAPI(
    title="AeroCraft API",
    description="AI-Powered Aerospace CAD Web Application",
    version="0.1.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(generation_router, prefix="/api")
app.include_router(export_router, prefix="/api")
app.include_router(images_router, prefix="/api")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "AeroCraft API",
        "version": "0.1.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )

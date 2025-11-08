from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
import aiofiles
import os
from pathlib import Path
import uuid
from app.core import settings
from app.models import ImageUploadResponse

router = APIRouter(prefix="/images", tags=["images"])

# Ensure upload directory exists
UPLOAD_DIR = Path(settings.upload_dir)
UPLOAD_DIR.mkdir(exist_ok=True)


@router.post("/upload", response_model=ImageUploadResponse)
async def upload_image(file: UploadFile = File(...)):
    """
    Upload a reference image.
    """
    try:
        # Validate file type
        if not file.content_type or not file.content_type.startswith('image/'):
            return ImageUploadResponse(
                success=False,
                error="File must be an image"
            )

        # Read file
        contents = await file.read()

        # Validate file size
        if len(contents) > settings.max_upload_size:
            return ImageUploadResponse(
                success=False,
                error="File size exceeds 10MB limit"
            )

        # Generate unique filename
        file_ext = os.path.splitext(file.filename or "image.jpg")[1]
        unique_filename = f"{uuid.uuid4()}{file_ext}"
        file_path = UPLOAD_DIR / unique_filename

        # Save file
        async with aiofiles.open(file_path, 'wb') as f:
            await f.write(contents)

        # Return URL (in production, use CDN or proper file serving)
        file_url = f"/api/images/{unique_filename}"

        return ImageUploadResponse(
            success=True,
            url=file_url
        )

    except Exception as e:
        print(f"Error uploading image: {e}")
        return ImageUploadResponse(
            success=False,
            error=str(e)
        )


@router.get("/{filename}")
async def get_image(filename: str):
    """
    Retrieve an uploaded image.
    """
    file_path = UPLOAD_DIR / filename

    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Image not found")

    return FileResponse(file_path)

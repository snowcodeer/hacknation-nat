from fastapi import APIRouter, HTTPException
from app.models import GenerateRequest, UpdateParametersRequest, GenerateResponse
from app.services import ai_service, geometry_service

router = APIRouter(prefix="/generate", tags=["generation"])

# In-memory storage for current model (in production, use database)
current_model = None


@router.post("/from-text", response_model=GenerateResponse)
async def generate_from_text(request: GenerateRequest):
    """
    Generate 3D model from text description using AI.
    """
    try:
        # Extract parameters from text using OpenAI
        parameters = await ai_service.extract_parameters_from_text(request.prompt)

        # Generate 3D model from parameters
        model = geometry_service.create_model_from_parameters(
            params=parameters,
            source_prompt=request.prompt,
            generated_from="text"
        )

        # Store in memory (temporary)
        global current_model
        current_model = model

        return GenerateResponse(
            success=True,
            model=model,
            parameters=parameters
        )

    except Exception as e:
        print(f"Error generating from text: {e}")
        return GenerateResponse(
            success=False,
            error=str(e)
        )


@router.post("/update-parameters", response_model=GenerateResponse)
async def update_parameters(request: UpdateParametersRequest):
    """
    Update current model with new parameters.
    """
    try:
        # Generate new model with updated parameters
        model = geometry_service.create_model_from_parameters(
            params=request.parameters,
            source_prompt=None,
            generated_from="manual"
        )

        # Store in memory
        global current_model
        current_model = model

        return GenerateResponse(
            success=True,
            model=model,
            parameters=request.parameters
        )

    except Exception as e:
        print(f"Error updating parameters: {e}")
        return GenerateResponse(
            success=False,
            error=str(e)
        )

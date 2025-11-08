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


@router.post("/compile-aircraft", response_model=GenerateResponse)
async def compile_aircraft(request: dict):
    """
    Compile all aircraft components into a single unified model.
    """
    try:
        aircraft_data = request.get('aircraft', {})

        # Extract all component models
        components = []
        component_names = []

        for component_type in ['wings', 'fuselage', 'tail_assembly', 'engines']:
            component = aircraft_data.get(component_type)
            if component and component.get('model'):
                components.append(component['model'])
                component_names.append(component_type)

        if len(components) < 4:
            return GenerateResponse(
                success=False,
                error="All 4 components must be generated before compiling"
            )

        # Compile the aircraft by merging geometries
        compiled_model = geometry_service.compile_aircraft_components(components, component_names)

        # Store in memory
        global current_model
        current_model = compiled_model

        return GenerateResponse(
            success=True,
            model=compiled_model
        )

    except Exception as e:
        print(f"Error compiling aircraft: {e}")
        import traceback
        traceback.print_exc()
        return GenerateResponse(
            success=False,
            error=str(e)
        )

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


@router.post("/from-chat")
async def generate_from_chat(request: GenerateRequest):
    """
    Generate complete aircraft from natural language chat description.
    Returns parameters for all 3 components (wings, fuselage, engines).
    """
    try:
        # Use AI to generate parameters for all components
        aircraft_params = await ai_service.generate_complete_aircraft(request.prompt)

        return {
            "success": True,
            "aircraft_params": aircraft_params
        }

    except Exception as e:
        print(f"Error generating from chat: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }


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

        for component_type in ['wings', 'fuselage', 'engines']:
            component = aircraft_data.get(component_type)
            if component and component.get('model'):
                components.append(component['model'])
                component_names.append(component_type)

        if len(components) < 3:
            return GenerateResponse(
                success=False,
                error="All 3 components must be generated before compiling"
            )

        # Compile the aircraft by merging geometries with AI-powered assembly
        compiled_model = await geometry_service.compile_aircraft_components(components, component_names, aircraft_data)

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


@router.post("/edit-component")
async def edit_component(request: dict):
    """
    Edit a component using natural language commands.
    Supports: size changes, rotation, position, and parameter updates.

    Example prompts:
    - "make the wings bigger"
    - "rotate the fuselage 45 degrees"
    - "move the engines forward"
    - "set wing span to 80 meters"
    """
    try:
        prompt = request.get('prompt')
        aircraft_data = request.get('aircraft', {})

        if not prompt:
            return {
                "success": False,
                "error": "No edit prompt provided"
            }

        # Use AI to parse the edit command
        edit_instruction = await ai_service.parse_edit_command(prompt, aircraft_data)

        component_type = edit_instruction.get('component')
        operation = edit_instruction.get('operation')
        parameters = edit_instruction.get('parameters', {})
        description = edit_instruction.get('description', '')

        print(f"[EDIT] Component: {component_type}, Operation: {operation}")
        print(f"[EDIT] Description: {description}")

        # Get the current component
        component = aircraft_data.get(component_type)
        if not component or not component.get('model'):
            return {
                "success": False,
                "error": f"Component '{component_type}' not found or not generated yet"
            }

        # Apply the edit based on operation type
        if operation == "parameter":
            # Regenerate component with updated parameter
            param_name = parameters.get('parameter_name')
            param_value = parameters.get('parameter_value')

            # Get current parameters and update the specified one
            current_params = component.get('parameters', {})

            # Convert to AeroParameters format
            from app.models import AeroParameters
            params_dict = dict(current_params)

            # Map parameter names to AeroParameters field names
            param_mapping = {
                'span': 'span',
                'root_chord': 'root_chord',
                'tip_chord': 'tip_chord',
                'sweep_angle': 'sweep_angle',
                'sweep': 'sweep_angle',
                'thickness': 'thickness',
                'dihedral': 'dihedral',
                'fuselage_length': 'fuselage_length',
                'fuselage_diameter': 'fuselage_diameter',
                'engine_length': 'engine_length',
                'engine_diameter': 'engine_diameter'
            }

            actual_param_name = param_mapping.get(param_name, param_name)
            params_dict[actual_param_name] = param_value

            # Regenerate the model with updated parameters
            updated_params = AeroParameters(**params_dict)
            updated_model = geometry_service.create_model_from_parameters(
                params=updated_params,
                source_prompt=f"Edited via chat: {prompt}",
                generated_from="edit"
            )

            return {
                "success": True,
                "component": component_type,
                "operation": operation,
                "description": description,
                "model": updated_model,
                "parameters": updated_params
            }

        elif operation == "scale":
            # Scale the component by modifying its dimensional parameters
            scale_factor = parameters.get('scale_factor', 1.0)

            # Get current parameters
            current_params = component.get('parameters', {})
            from app.models import AeroParameters
            params_dict = dict(current_params)

            # Scale the appropriate dimensional parameters based on component type
            if component_type == "wings":
                # Scale wing dimensions
                if 'span' in params_dict:
                    params_dict['span'] = params_dict['span'] * scale_factor
                if 'root_chord' in params_dict:
                    params_dict['root_chord'] = params_dict['root_chord'] * scale_factor
                if 'tip_chord' in params_dict:
                    params_dict['tip_chord'] = params_dict['tip_chord'] * scale_factor

            elif component_type == "fuselage":
                # Scale fuselage dimensions
                if 'fuselage_length' in params_dict and params_dict['fuselage_length']:
                    params_dict['fuselage_length'] = params_dict['fuselage_length'] * scale_factor
                if 'fuselage_diameter' in params_dict and params_dict['fuselage_diameter']:
                    params_dict['fuselage_diameter'] = params_dict['fuselage_diameter'] * scale_factor
                # Also scale the root/tip chord to match fuselage length
                if 'root_chord' in params_dict:
                    params_dict['root_chord'] = params_dict['root_chord'] * scale_factor
                if 'tip_chord' in params_dict:
                    params_dict['tip_chord'] = params_dict['tip_chord'] * scale_factor

            elif component_type == "engines":
                # Scale engine dimensions
                if 'engine_length' in params_dict and params_dict['engine_length']:
                    params_dict['engine_length'] = params_dict['engine_length'] * scale_factor
                if 'engine_diameter' in params_dict and params_dict['engine_diameter']:
                    params_dict['engine_diameter'] = params_dict['engine_diameter'] * scale_factor
                # Also scale the root/tip chord to match engine length
                if 'root_chord' in params_dict:
                    params_dict['root_chord'] = params_dict['root_chord'] * scale_factor
                if 'tip_chord' in params_dict:
                    params_dict['tip_chord'] = params_dict['tip_chord'] * scale_factor

            # Regenerate the model with scaled parameters
            updated_params = AeroParameters(**params_dict)
            updated_model = geometry_service.create_model_from_parameters(
                params=updated_params,
                source_prompt=f"Scaled via chat: {prompt}",
                generated_from="edit"
            )

            return {
                "success": True,
                "component": component_type,
                "operation": operation,
                "description": description,
                "model": updated_model,
                "parameters": updated_params
            }

        elif operation in ["rotate", "translate"]:
            # For geometric transformations, we need to modify the geometry
            # This is more complex as we need to transform the vertices
            return {
                "success": False,
                "error": f"Operation '{operation}' not yet implemented. Use parameter changes for now (e.g., 'set wing span to X meters')"
            }

        else:
            return {
                "success": False,
                "error": f"Unknown operation: {operation}"
            }

    except Exception as e:
        print(f"Error editing component: {e}")
        import traceback
        traceback.print_exc()
        return {
            "success": False,
            "error": str(e)
        }

"""
Refactored Geometry Service using SOLID principles.
Delegates component generation to specialized generators.
"""
import numpy as np
import trimesh
from typing import Tuple
from app.models import AeroParameters, GeometryData, Model3D, ModelMetadata
from datetime import datetime
import uuid
import sys

# Import generator factory for component generation
from app.services.generators import GeneratorFactory


class GeometryService:
    """
    Service for creating 3D geometry models.

    Following SOLID principles:
    - Single Responsibility: Coordinates geometry generation and model creation
    - Open/Closed: Extensible via new generators without modifying this service
    - Dependency Inversion: Depends on abstract ComponentGenerator interface

    Responsibilities:
    - Determine component type from parameters
    - Delegate mesh generation to specialized generators
    - Create Model3D objects with metadata
    - Compile multiple components into complete aircraft
    """

    def __init__(self):
        """Initialize geometry service with generator factory."""
        self.generator_factory = GeneratorFactory

    def create_model_from_parameters(
        self,
        params: AeroParameters,
        source_prompt: str = None,
        generated_from: str = "text"
    ) -> Model3D:
        """
        Create a complete Model3D from parameters.

        Args:
            params: Component parameters
            source_prompt: Original text prompt (optional)
            generated_from: Generation source ("text", "manual", etc.)

        Returns:
            Model3D: Complete 3D model with geometry and metadata
        """
        # Determine component type and get appropriate generator
        component_type = self._determine_component_type(params, source_prompt)

        print(f"DEBUG: source_prompt='{source_prompt}'", file=sys.stderr, flush=True)
        print(f"DEBUG: determined component_type='{component_type}'", file=sys.stderr, flush=True)

        # Get generator from factory
        generator = self.generator_factory.create(component_type)

        if not generator:
            raise ValueError(f"No generator available for component type: {component_type}")

        # Generate mesh using specialized generator
        print(f"DEBUG: Generating {component_type.upper()} mesh using {generator.__class__.__name__}", file=sys.stderr, flush=True)
        mesh = generator.generate(params)

        # Convert to geometry data
        geometry = GeometryData(
            vertices=mesh.vertices.flatten().tolist(),
            indices=mesh.faces.flatten().tolist(),
            normals=mesh.vertex_normals.flatten().tolist()
        )

        # Create metadata
        metadata = ModelMetadata(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            generated_from=generated_from,
            source_prompt=source_prompt
        )

        # Determine component name
        component_name = self._determine_component_name(params, source_prompt)

        # Create model
        model = Model3D(
            id=str(uuid.uuid4()),
            name=component_name,
            parameters=params,
            geometry=geometry,
            metadata=metadata
        )

        return model

    def _determine_component_type(self, params: AeroParameters, source_prompt: str = None) -> str:
        """
        Determine the component type (wing, fuselage, tail, engine) based on parameters and prompt.
        Uses modular parameter approach - engines have engine_* fields, fuselages have fuselage_* fields.

        Args:
            params: Component parameters
            source_prompt: Original text prompt (optional)

        Returns:
            str: Component type identifier ("wing", "fuselage", "tail", "engine")
        """
        prompt_lower = (source_prompt or "").lower()

        # Check prompt for explicit component type keywords (highest priority)
        if "fuselage" in prompt_lower or "body" in prompt_lower:
            return "fuselage"
        elif "tail" in prompt_lower or "stabilizer" in prompt_lower:
            return "tail"
        elif "engine" in prompt_lower or "nacelle" in prompt_lower or "turbine" in prompt_lower:
            return "engine"
        elif "wing" in prompt_lower or "wings" in prompt_lower:
            return "wing"

        # Check for tail indicators
        if params.has_vertical_stabilizer or params.has_horizontal_stabilizer:
            return "tail"

        # MODULAR APPROACH: Check for ENGINE parameters (engine_length, engine_diameter)
        if params.engine_length and params.engine_diameter:
            return "engine"

        # MODULAR APPROACH: Check for FUSELAGE parameters (fuselage_length, fuselage_diameter)
        if params.fuselage_length and params.fuselage_diameter:
            return "fuselage"

        # Fallback: Check thickness and span for old parameters
        if params.thickness > 70 and params.span < 1.0:
            # Very thick with small span - likely engine or fuselage
            # But without specific parameters, default to fuselage
            return "fuselage"

        # Default to wing
        return "wing"

    def _determine_component_name(self, params: AeroParameters, source_prompt: str = None) -> str:
        """
        Determine the component name based on parameters and source prompt.

        Args:
            params: Component parameters
            source_prompt: Original text prompt (optional)

        Returns:
            str: Human-readable component name
        """
        component_type = self._determine_component_type(params, source_prompt)

        if component_type == "fuselage":
            fuselage_type = (params.fuselage_type or "commercial").capitalize()
            return f"{fuselage_type} Fuselage"
        elif component_type == "tail":
            return "Tail Assembly"
        elif component_type == "engine":
            return "Engine Nacelle"
        else:  # wing
            return f"{params.wing_type.capitalize()} Wing"

    def compile_aircraft_components(self, components: list, component_names: list) -> Model3D:
        """
        Compile multiple aircraft components into a single unified model.
        Positions components correctly in 3D space to form a realistic aircraft.

        Args:
            components: List of component models or dicts
            component_names: List of component type names

        Returns:
            Model3D: Compiled aircraft model
        """
        # Create trimesh objects from components with proper positioning
        meshes = []

        # Extract component meshes
        wings_mesh = None
        fuselage_mesh = None
        tail_mesh = None
        engines_mesh = None

        for i, component in enumerate(components):
            print(f"DEBUG: Component {i} type: {type(component)}", file=sys.stderr, flush=True)
            print(f"DEBUG: Component {i} keys: {component.keys() if isinstance(component, dict) else 'not a dict'}", file=sys.stderr, flush=True)

            # Handle both dict and Model3D object
            if isinstance(component, dict):
                geometry = component.get('geometry')
            else:
                # Assume it's a Model3D object with .geometry attribute
                geometry = component.geometry if hasattr(component, 'geometry') else component

            print(f"DEBUG: Geometry type: {type(geometry)}", file=sys.stderr, flush=True)

            # Convert geometry data to numpy arrays
            # Handle both dict and GeometryData object
            if isinstance(geometry, dict):
                vertices_data = geometry['vertices']
                indices_data = geometry['indices']
            else:
                vertices_data = geometry.vertices if hasattr(geometry, 'vertices') else geometry
                indices_data = geometry.indices if hasattr(geometry, 'indices') else geometry

            # Handle case where vertices/indices are dicts with string keys (from JSON)
            if isinstance(vertices_data, dict):
                # Convert dict to list by sorting keys numerically
                vertices_list = [vertices_data[str(i)] for i in sorted([int(k) for k in vertices_data.keys()])]
                vertices_data = vertices_list
                print(f"DEBUG: Converted vertices dict to list, length: {len(vertices_list)}", file=sys.stderr, flush=True)

            if isinstance(indices_data, dict):
                # Convert dict to list by sorting keys numerically
                indices_list = [indices_data[str(i)] for i in sorted([int(k) for k in indices_data.keys()])]
                indices_data = indices_list
                print(f"DEBUG: Converted indices dict to list, length: {len(indices_list)}", file=sys.stderr, flush=True)

            vertices = np.array(vertices_data, dtype=np.float32).reshape(-1, 3)
            indices = np.array(indices_data, dtype=np.int32).reshape(-1, 3)

            # Create mesh
            mesh = trimesh.Trimesh(vertices=vertices, faces=indices)

            # Assign to appropriate component based on name
            component_type = component_names[i].lower()
            if 'wing' in component_type:
                wings_mesh = mesh
            elif 'fuselage' in component_type:
                fuselage_mesh = mesh
            elif 'tail' in component_type:
                tail_mesh = mesh
            elif 'engine' in component_type:
                engines_mesh = mesh

        # Position components to form a realistic aircraft
        positioned_meshes = []

        # 1. Fuselage - center of aircraft (reference point)
        if fuselage_mesh:
            positioned_meshes.append(fuselage_mesh)
            fuselage_bounds = fuselage_mesh.bounds
            fuselage_length = fuselage_bounds[1][0] - fuselage_bounds[0][0]
        else:
            fuselage_length = 4.0  # Default length if no fuselage

        # 2. Wings - attach at 1/3 from nose (forward part of fuselage)
        # Create left and right wings
        if wings_mesh:
            wing_offset_x = -fuselage_length * 0.15  # Slightly forward of center
            wing_offset_y = 0  # Distance from centerline (will be positive for right, negative for left)
            wing_offset_z = 0  # At fuselage centerline

            # Assuming wings_mesh is a single wing, duplicate it for left and right
            # Right wing (positive Y)
            translation_right = trimesh.transformations.translation_matrix([wing_offset_x, wing_offset_y, wing_offset_z])
            wing_right = wings_mesh.copy()
            wing_right.apply_transform(translation_right)
            positioned_meshes.append(wing_right)

            # Left wing (negative Y) - mirror across XZ plane
            wing_left = wings_mesh.copy()
            # Mirror by scaling Y by -1
            mirror_matrix = np.diag([1, -1, 1, 1])
            wing_left.apply_transform(mirror_matrix)
            translation_left = trimesh.transformations.translation_matrix([wing_offset_x, -wing_offset_y, wing_offset_z])
            wing_left.apply_transform(translation_left)
            positioned_meshes.append(wing_left)

        # 3. Tail Assembly - attach at rear of fuselage
        if tail_mesh:
            tail_offset_x = fuselage_length * 0.4  # At rear
            tail_offset_z = 0  # Align with fuselage top
            translation = trimesh.transformations.translation_matrix([tail_offset_x, 0, tail_offset_z])
            tail_positioned = tail_mesh.copy()
            tail_positioned.apply_transform(translation)
            positioned_meshes.append(tail_positioned)

        # 4. Engines - attach under wings or on fuselage sides
        if engines_mesh:
            # Create two engines (left and right)
            # Position engines under the wings, not at the tips
            engine_offset_x = -fuselage_length * 0.15  # Slightly forward (closer to wing position)

            # Calculate engine position based on wing span if available
            # Typical placement is 30-40% of semi-span from centerline
            if wings_mesh:
                wing_bounds = wings_mesh.bounds
                wing_semi_span = (wing_bounds[1][1] - wing_bounds[0][1]) / 2  # Half the Y extent
                engine_offset_y = wing_semi_span * 0.35  # 35% of semi-span from centerline
            else:
                engine_offset_y = 5.0  # Default fallback if no wings

            engine_offset_z = -0.5  # Below wing/fuselage

            # Rotate engine 90 degrees around Y-axis to make it horizontal (pointing forward)
            rotation_matrix = trimesh.transformations.rotation_matrix(
                np.radians(90),  # 90 degrees
                [0, 1, 0]  # Around Y-axis
            )

            # Left engine
            translation_left = trimesh.transformations.translation_matrix([engine_offset_x, engine_offset_y, engine_offset_z])
            engine_left = engines_mesh.copy()
            engine_left.apply_transform(rotation_matrix)  # Rotate first
            engine_left.apply_transform(translation_left)  # Then translate
            positioned_meshes.append(engine_left)

            # Right engine
            translation_right = trimesh.transformations.translation_matrix([engine_offset_x, -engine_offset_y, engine_offset_z])
            engine_right = engines_mesh.copy()
            engine_right.apply_transform(rotation_matrix)  # Rotate first
            engine_right.apply_transform(translation_right)  # Then translate
            positioned_meshes.append(engine_right)

        # Combine all positioned meshes
        if len(positioned_meshes) > 1:
            combined_mesh = trimesh.util.concatenate(positioned_meshes)
        elif len(positioned_meshes) == 1:
            combined_mesh = positioned_meshes[0]
        else:
            # Fallback: create a simple placeholder
            combined_mesh = trimesh.creation.box()

        # Convert combined mesh to geometry data
        all_vertices = combined_mesh.vertices.flatten().tolist()
        all_indices = combined_mesh.faces.flatten().tolist()

        # Calculate normals
        try:
            all_normals = combined_mesh.vertex_normals.flatten().tolist()
        except:
            all_normals = []

        # Create combined geometry data
        combined_geometry = GeometryData(
            vertices=all_vertices,
            indices=all_indices,
            normals=all_normals if all_normals else None
        )

        # Create metadata
        metadata = ModelMetadata(
            created_at=datetime.now(),
            updated_at=datetime.now(),
            generated_from="compilation",
            source_prompt=f"Compiled aircraft from {len(components)} components: {', '.join(component_names)}"
        )

        # Use first component's parameters as base (or create default)
        base_params = components[0]['parameters'] if components else AeroParameters(
            wing_type="compiled",
            span=0,
            root_chord=0,
            sweep_angle=0,
            thickness=0,
            dihedral=0
        )

        # Create compiled model
        compiled_model = Model3D(
            id=str(uuid.uuid4()),
            name="Complete Aircraft",
            parameters=base_params,
            geometry=combined_geometry,
            metadata=metadata
        )

        return compiled_model


# Singleton instance
geometry_service = GeometryService()

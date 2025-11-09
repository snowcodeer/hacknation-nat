import numpy as np
import trimesh
from typing import Tuple
from app.models import AeroParameters, GeometryData, Model3D, ModelMetadata
from datetime import datetime
import uuid
import sys


class GeometryService:
    def generate_wing_mesh(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Generate a 3D wing mesh based on parameters.
        Creates a simple but realistic wing geometry.
        """
        if params.wing_type == "delta":
            return self._create_delta_wing(params)
        elif params.wing_type == "swept":
            return self._create_swept_wing(params)
        elif params.wing_type == "straight":
            return self._create_straight_wing(params)
        elif params.wing_type == "tapered":
            return self._create_tapered_wing(params)
        else:
            return self._create_delta_wing(params)

    def _create_delta_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """Create a single wing half (from root to tip) for proper assembly with flat mounting edge"""
        half_span = params.span / 2
        root_chord = params.root_chord
        tip_chord = (params.tip_chord or 0.1)
        thickness_ratio = params.thickness / 100
        sweep_rad = np.radians(params.sweep_angle)
        dihedral_rad = np.radians(params.dihedral)

        # Define wing profile points (airfoil approximation)
        num_chord = 20
        num_span = 15

        vertices = []
        faces = []

        # Generate vertices for upper and lower surfaces (single wing half only)
        for i in range(num_span):
            t = i / (num_span - 1)  # 0 to 1 from root to tip

            # Current span position (only positive Y - single wing half)
            y = half_span * t
            y_dihedral = y * np.sin(dihedral_rad)
            z_dihedral = y * (1 - np.cos(dihedral_rad))

            # Chord at this span position (linear taper)
            chord = root_chord + (tip_chord - root_chord) * t

            # Sweep offset
            x_sweep = y * np.tan(sweep_rad)

            # Generate airfoil profile at this span position
            for j in range(num_chord):
                x_chord = (j / (num_chord - 1))  # 0 to 1 along chord
                x = x_sweep + x_chord * chord - root_chord / 2  # Center the wing

                # Simple airfoil shape (approximation)
                if x_chord < 0.3:
                    z_upper = thickness_ratio * chord * (0.6 * x_chord / 0.3)
                elif x_chord < 0.6:
                    z_upper = thickness_ratio * chord * 0.6
                else:
                    z_upper = thickness_ratio * chord * 0.6 * (1 - x_chord) / 0.4

                z_lower = -z_upper * 0.5  # Asymmetric airfoil

                # Upper surface
                vertices.append([x, y_dihedral, z_dihedral + z_upper])
                # Lower surface
                vertices.append([x, y_dihedral, z_dihedral + z_lower])

        # Create flat root edge (where wing attaches to fuselage)
        # Add vertices along the root chord to create a flat vertical surface
        for j in range(num_chord):
            x_chord = (j / (num_chord - 1))
            x = x_chord * root_chord - root_chord / 2

            # Get the airfoil thickness at root
            if x_chord < 0.3:
                z_upper = thickness_ratio * root_chord * (0.6 * x_chord / 0.3)
            elif x_chord < 0.6:
                z_upper = thickness_ratio * root_chord * 0.6
            else:
                z_upper = thickness_ratio * root_chord * 0.6 * (1 - x_chord) / 0.4

            z_lower = -z_upper * 0.5

            # These vertices are already in the list at i=0, but we need them for the flat edge

        vertices_array = np.array(vertices, dtype=np.float32)

        # Generate faces (triangles) for single wing half only
        for i in range(num_span - 1):
            for j in range(num_chord - 1):
                # Indices for quad
                idx = i * num_chord * 2 + j * 2

                # Upper surface triangles
                v1 = idx
                v2 = idx + 2
                v3 = idx + num_chord * 2
                v4 = idx + num_chord * 2 + 2

                faces.append([v1, v2, v3])
                faces.append([v2, v4, v3])

                # Lower surface triangles
                v1_l = idx + 1
                v2_l = idx + 3
                v3_l = idx + num_chord * 2 + 1
                v4_l = idx + num_chord * 2 + 3

                faces.append([v1_l, v3_l, v2_l])
                faces.append([v2_l, v3_l, v4_l])

        # Add root edge cap (flat vertical surface at fuselage attachment)
        # This creates a flat rectangular edge where the wing meets the fuselage
        for j in range(num_chord - 1):
            # Connect upper and lower surfaces at root (i=0) to form flat edge
            upper_curr = j * 2
            lower_curr = j * 2 + 1
            upper_next = (j + 1) * 2
            lower_next = (j + 1) * 2 + 1

            # Two triangles to form the rectangular edge quad
            faces.append([upper_curr, lower_curr, upper_next])
            faces.append([lower_curr, lower_next, upper_next])

        # Add tip edge cap
        tip_start = (num_span - 1) * num_chord * 2
        for j in range(num_chord - 1):
            upper_curr = tip_start + j * 2
            lower_curr = tip_start + j * 2 + 1
            upper_next = tip_start + (j + 1) * 2
            lower_next = tip_start + (j + 1) * 2 + 1

            faces.append([upper_curr, upper_next, lower_curr])
            faces.append([lower_curr, upper_next, lower_next])

        faces_array = np.array(faces, dtype=np.int32)

        # Create trimesh
        mesh = trimesh.Trimesh(vertices=vertices_array, faces=faces_array)
        mesh.fix_normals()

        return mesh

    def _create_swept_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """Create a swept wing (similar to delta but with different proportions)"""
        # Reuse delta wing logic with modifications
        return self._create_delta_wing(params)

    def _create_straight_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """Create a straight wing (no sweep, rectangular - no taper)"""
        params_copy = params.model_copy()
        params_copy.sweep_angle = 0
        # For truly rectangular wings, tip chord equals root chord (no taper)
        params_copy.tip_chord = params_copy.root_chord
        return self._create_delta_wing(params_copy)

    def _create_tapered_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """Create a tapered wing"""
        return self._create_delta_wing(params)

    def generate_fuselage_mesh(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Generate a 3D cylindrical or tapered fuselage mesh using MODULAR fuselage parameters.
        Creates a realistic fuselage body with realistic dimensions.
        """
        # Use MODULAR FUSELAGE PARAMETERS - fuselages have their own fields
        length = params.fuselage_length or params.root_chord or 5.0  # Default 5m if not specified
        diameter = params.fuselage_diameter or 0.8  # Default 0.8m if not specified

        # Create a cylindrical fuselage with nose cone and tail cone
        num_segments = 32  # Circular resolution
        num_length_segments = 30  # Length resolution

        vertices = []
        faces = []

        # Generate fuselage from nose to tail
        for i in range(num_length_segments + 1):
            t = i / num_length_segments  # 0 (nose) to 1 (tail)
            x = (t - 0.5) * length  # Center at origin

            # Variable radius along length (nose cone, main body, tail cone)
            if t < 0.15:  # Nose cone
                radius = diameter / 2 * (t / 0.15) ** 0.5
            elif t > 0.85:  # Tail cone
                radius = diameter / 2 * ((1 - t) / 0.15) ** 0.7
            else:  # Main cylindrical body
                radius = diameter / 2

            # Create circular cross-section
            for j in range(num_segments):
                angle = 2 * np.pi * j / num_segments
                y = radius * np.cos(angle)
                z = radius * np.sin(angle)
                vertices.append([x, y, z])

        # Generate faces connecting the rings
        for i in range(num_length_segments):
            for j in range(num_segments):
                # Current ring indices
                current = i * num_segments + j
                next_in_ring = i * num_segments + (j + 1) % num_segments
                next_ring = (i + 1) * num_segments + j
                next_ring_next = (i + 1) * num_segments + (j + 1) % num_segments

                # Two triangles per quad
                faces.append([current, next_ring, next_in_ring])
                faces.append([next_in_ring, next_ring, next_ring_next])

        vertices_array = np.array(vertices, dtype=np.float32)
        faces_array = np.array(faces, dtype=np.int32)

        mesh = trimesh.Trimesh(vertices=vertices_array, faces=faces_array)
        mesh.fix_normals()

        return mesh

    def generate_engine_mesh(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Generate a 3D engine nacelle mesh using MODULAR engine parameters.
        Creates cylindrical engine pods with realistic dimensions.
        """
        # Use MODULAR ENGINE PARAMETERS - engines have their own fields
        length = params.engine_length or 2.0  # Default 2m if not specified
        diameter = params.engine_diameter or 0.5  # Default 0.5m if not specified

        # Create engine nacelle (simplified jet engine)
        num_segments = 24
        num_length_segments = 20

        vertices = []
        faces = []

        for i in range(num_length_segments + 1):
            t = i / num_length_segments
            x = (t - 0.5) * length

            # Variable radius for engine shape (intake larger, exhaust smaller)
            if t < 0.2:  # Intake
                radius = diameter / 2 * (1 + 0.3 * (1 - t / 0.2))
            elif t > 0.8:  # Exhaust nozzle
                radius = diameter / 2 * (0.9 - 0.2 * (t - 0.8) / 0.2)
            else:  # Main engine body
                radius = diameter / 2

            # Create circular cross-section
            for j in range(num_segments):
                angle = 2 * np.pi * j / num_segments
                y = radius * np.cos(angle)
                z = radius * np.sin(angle)
                vertices.append([x, y, z])

        # Generate faces
        for i in range(num_length_segments):
            for j in range(num_segments):
                current = i * num_segments + j
                next_in_ring = i * num_segments + (j + 1) % num_segments
                next_ring = (i + 1) * num_segments + j
                next_ring_next = (i + 1) * num_segments + (j + 1) % num_segments

                faces.append([current, next_ring, next_in_ring])
                faces.append([next_in_ring, next_ring, next_ring_next])

        vertices_array = np.array(vertices, dtype=np.float32)
        faces_array = np.array(faces, dtype=np.int32)

        mesh = trimesh.Trimesh(vertices=vertices_array, faces=faces_array)
        mesh.fix_normals()

        return mesh

    def generate_tail_mesh(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Generate a 3D tail assembly with vertical and horizontal stabilizers.
        Always creates both stabilizers to form a proper T-tail or cruciform configuration.
        """
        meshes = []

        # Horizontal stabilizer (smaller wing-like structure)
        # Proportional to main wing size (AI generates realistic dimensions)
        h_stab_params = params.model_copy()
        h_stab_params.span = params.span * 0.6  # 60% of main wing span
        h_stab_params.root_chord = params.root_chord * 0.4  # 40% of main wing chord
        h_stab_params.tip_chord = params.tip_chord * 0.4 if params.tip_chord else params.root_chord * 0.2
        h_stab_params.sweep_angle = params.sweep_angle * 0.7
        h_stab_params.thickness = params.thickness * 0.8

        horizontal_mesh = self._create_delta_wing(h_stab_params)
        meshes.append(horizontal_mesh)

        # Vertical stabilizer (taller, narrower)
        v_stab_params = params.model_copy()
        v_stab_params.span = params.span * 0.5  # 50% of main wing span (becomes height)
        v_stab_params.root_chord = params.root_chord * 0.5  # 50% of main wing chord
        v_stab_params.tip_chord = params.tip_chord * 0.3 if params.tip_chord else params.root_chord * 0.2
        v_stab_params.sweep_angle = params.sweep_angle * 0.8
        v_stab_params.thickness = params.thickness * 0.9
        v_stab_params.dihedral = 0

        # Create and rotate 90 degrees to make it vertical
        vertical_mesh = self._create_delta_wing(v_stab_params)

        # Rotate around X-axis by 90 degrees to make it vertical
        rotation_matrix = trimesh.transformations.rotation_matrix(
            np.pi / 2,  # 90 degrees
            [1, 0, 0]  # Around X-axis
        )
        vertical_mesh.apply_transform(rotation_matrix)

        # Shift it upward to form T-tail configuration
        vertical_mesh.vertices[:, 2] += params.span * 0.15  # Position above horizontal stabilizer

        meshes.append(vertical_mesh)

        # Combine both stabilizers into one mesh
        combined_mesh = trimesh.util.concatenate(meshes)

        return combined_mesh

    def create_model_from_parameters(
        self,
        params: AeroParameters,
        source_prompt: str = None,
        generated_from: str = "text"
    ) -> Model3D:
        """
        Create a complete Model3D from parameters.
        """
        # Determine component type and generate appropriate mesh
        component_type = self._determine_component_type(params, source_prompt)

        print(f"DEBUG: source_prompt='{source_prompt}'", file=sys.stderr, flush=True)
        print(f"DEBUG: determined component_type='{component_type}'", file=sys.stderr, flush=True)
        print(f"DEBUG: params.fuselage_length={params.fuselage_length}, params.fuselage_diameter={params.fuselage_diameter}", file=sys.stderr, flush=True)
        print(f"DEBUG: params.has_vertical_stabilizer={params.has_vertical_stabilizer}, params.has_horizontal_stabilizer={params.has_horizontal_stabilizer}", file=sys.stderr, flush=True)

        if component_type == "fuselage":
            print("DEBUG: Generating FUSELAGE mesh", file=sys.stderr, flush=True)
            mesh = self.generate_fuselage_mesh(params)
        elif component_type == "engine":
            print("DEBUG: Generating ENGINE mesh", file=sys.stderr, flush=True)
            mesh = self.generate_engine_mesh(params)
        elif component_type == "tail":
            print("DEBUG: Generating TAIL mesh", file=sys.stderr, flush=True)
            mesh = self.generate_tail_mesh(params)
        else:  # wing
            print("DEBUG: Generating WING mesh", file=sys.stderr, flush=True)
            mesh = self.generate_wing_mesh(params)

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

        # Determine component type based on parameters
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
        Returns: "wing", "fuselage", "tail", or "engine"
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
        """
        component_type = self._determine_component_type(params, source_prompt)

        if component_type == "fuselage":
            return f"{params.wing_type.capitalize()} Fuselage"
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
            print(f"DEBUG: Geometry: {geometry}", file=sys.stderr, flush=True)

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
            engine_offset_x = -fuselage_length * 0.1  # Slightly forward
            engine_offset_y = 0.8  # Distance from centerline
            engine_offset_z = -0.3  # Below wing/fuselage

            # Left engine
            translation_left = trimesh.transformations.translation_matrix([engine_offset_x, engine_offset_y, engine_offset_z])
            engine_left = engines_mesh.copy()
            engine_left.apply_transform(translation_left)
            positioned_meshes.append(engine_left)

            # Right engine
            translation_right = trimesh.transformations.translation_matrix([engine_offset_x, -engine_offset_y, engine_offset_z])
            engine_right = engines_mesh.copy()
            engine_right.apply_transform(translation_right)
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


geometry_service = GeometryService()

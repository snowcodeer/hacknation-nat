import numpy as np
import trimesh
from typing import Tuple
from app.models import AeroParameters, GeometryData, Model3D, ModelMetadata
from datetime import datetime
import uuid


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
        """Create a delta wing shape"""
        half_span = params.span / 2
        root_chord = params.root_chord
        tip_chord = params.tip_chord or 0.1
        thickness_ratio = params.thickness / 100
        sweep_rad = np.radians(params.sweep_angle)
        dihedral_rad = np.radians(params.dihedral)

        # Define wing profile points (airfoil approximation)
        num_chord = 20
        num_span = 15

        vertices = []
        faces = []

        # Generate vertices for upper and lower surfaces
        for i in range(num_span):
            t = i / (num_span - 1)  # 0 to 1 from root to tip

            # Current span position
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

        # Mirror for other wing half
        mirrored_vertices = []
        for v in vertices:
            mirrored_vertices.append([v[0], -v[1], v[2]])

        all_vertices = vertices + mirrored_vertices
        vertices_array = np.array(all_vertices, dtype=np.float32)

        # Generate faces (triangles)
        vertex_count_half = len(vertices)

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

        # Repeat for mirrored half
        for i in range(num_span - 1):
            for j in range(num_chord - 1):
                idx = i * num_chord * 2 + j * 2 + vertex_count_half

                v1 = idx
                v2 = idx + 2
                v3 = idx + num_chord * 2
                v4 = idx + num_chord * 2 + 2

                faces.append([v1, v2, v3])
                faces.append([v2, v4, v3])

                v1_l = idx + 1
                v2_l = idx + 3
                v3_l = idx + num_chord * 2 + 1
                v4_l = idx + num_chord * 2 + 3

                faces.append([v1_l, v3_l, v2_l])
                faces.append([v2_l, v3_l, v4_l])

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
        """Create a straight wing (no sweep)"""
        params_copy = params.model_copy()
        params_copy.sweep_angle = 0
        return self._create_delta_wing(params_copy)

    def _create_tapered_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """Create a tapered wing"""
        return self._create_delta_wing(params)

    def create_model_from_parameters(
        self,
        params: AeroParameters,
        source_prompt: str = None,
        generated_from: str = "text"
    ) -> Model3D:
        """
        Create a complete Model3D from parameters.
        """
        # Generate mesh
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

    def _determine_component_name(self, params: AeroParameters, source_prompt: str = None) -> str:
        """
        Determine the component name based on parameters and source prompt.
        """
        prompt_lower = (source_prompt or "").lower()

        # Check for fuselage indicators
        if params.fuselage_length and params.fuselage_diameter:
            if params.fuselage_diameter > 0.5:  # Significant diameter
                return f"{params.wing_type.capitalize()} Fuselage"

        # Check prompt for component type keywords
        if "fuselage" in prompt_lower:
            return f"{params.wing_type.capitalize()} Fuselage"
        elif "tail" in prompt_lower or "stabilizer" in prompt_lower:
            return "Tail Assembly"
        elif "engine" in prompt_lower:
            return "Engine"
        elif "wing" in prompt_lower or "wings" in prompt_lower:
            return f"{params.wing_type.capitalize()} Wing"

        # Default based on parameters
        if params.thickness > 70:  # Very thick - likely fuselage
            return f"{params.wing_type.capitalize()} Fuselage"
        else:
            return f"{params.wing_type.capitalize()} Wing"


    def compile_aircraft_components(self, components: list, component_names: list) -> Model3D:
        """
        Compile multiple aircraft components into a single unified model.
        Merges all geometries into one combined mesh.
        """
        all_vertices = []
        all_indices = []
        all_normals = []
        vertex_offset = 0

        # Merge all component geometries
        for component in components:
            geometry = component['geometry']

            print(f"DEBUG: Processing component, geometry keys: {geometry.keys()}")
            print(f"DEBUG: Vertices type: {type(geometry['vertices'])}, first item: {type(geometry['vertices'][0]) if geometry['vertices'] else None}")
            print(f"DEBUG: Indices type: {type(geometry['indices'])}, first item: {type(geometry['indices'][0]) if geometry['indices'] else None}")

            # Get vertices
            vertices = geometry['vertices']
            if not isinstance(vertices, list):
                vertices = vertices.tolist() if hasattr(vertices, 'tolist') else list(vertices)
            # Ensure vertices are floats
            vertices = [float(v) for v in vertices]

            # Get indices
            indices = geometry['indices']
            if not isinstance(indices, list):
                indices = indices.tolist() if hasattr(indices, 'tolist') else list(indices)
            # Ensure indices are integers
            indices = [int(i) for i in indices]

            print(f"DEBUG: After conversion - vertex_offset type: {type(vertex_offset)}, first index: {indices[0] if indices else None}, type: {type(indices[0]) if indices else None}")

            # Get normals
            normals = geometry.get('normals', [])
            if normals and not isinstance(normals, list):
                normals = normals.tolist() if hasattr(normals, 'tolist') else list(normals)
            # Ensure normals are floats
            if normals:
                normals = [float(n) for n in normals]

            # Append vertices and normals
            all_vertices.extend(vertices)
            if normals:
                all_normals.extend(normals)

            # Append indices with offset
            for idx in indices:
                all_indices.append(idx + vertex_offset)

            # Update offset (vertices are grouped by 3, so divide by 3)
            vertex_offset += len(vertices) // 3

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

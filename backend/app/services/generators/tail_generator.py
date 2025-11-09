"""
Tail assembly component generator.
Single Responsibility: Generates only tail geometry (horizontal + vertical stabilizers).
"""
import numpy as np
import trimesh
from app.models import AeroParameters
from app.services.generators.base_generator import ComponentGenerator


class TailGenerator(ComponentGenerator):
    """
    Generates tail assembly meshes with horizontal and vertical stabilizers.

    Responsibilities:
    - Generate tail geometry from parameters
    - Create horizontal stabilizer (smaller wing-like)
    - Create vertical stabilizer (fin)
    - Combine into T-tail or cruciform configuration
    - Validate tail-specific parameters
    """

    def get_component_type(self) -> str:
        return "tail"

    def validate_parameters(self, params: AeroParameters) -> bool:
        """Validate tail parameters."""
        # Tail uses wing-based parameters for proportions
        if params.span <= 0:
            return False
        if params.root_chord <= 0:
            return False
        return True

    def generate(self, params: AeroParameters) -> trimesh.Trimesh:
        """Generate tail assembly mesh with both stabilizers."""
        if not self.validate_parameters(params):
            raise ValueError("Invalid tail parameters")

        meshes = []

        # 1. Horizontal stabilizer (smaller wing-like structure)
        horizontal_mesh = self._create_horizontal_stabilizer(params)
        meshes.append(horizontal_mesh)

        # 2. Vertical stabilizer (fin)
        vertical_mesh = self._create_vertical_stabilizer(params)
        meshes.append(vertical_mesh)

        # Combine both stabilizers into one mesh
        combined_mesh = trimesh.util.concatenate(meshes)

        return combined_mesh

    def _create_horizontal_stabilizer(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Create horizontal stabilizer (proportional to main wing).

        Args:
            params: Base aircraft parameters

        Returns:
            trimesh.Trimesh: Horizontal stabilizer mesh
        """
        # Scale parameters for horizontal stabilizer (60% of main wing)
        h_stab_params = params.model_copy()
        h_stab_params.span = params.span * 0.6
        h_stab_params.root_chord = params.root_chord * 0.4
        h_stab_params.tip_chord = params.tip_chord * 0.4 if params.tip_chord else params.root_chord * 0.2
        h_stab_params.sweep_angle = params.sweep_angle * 0.7
        h_stab_params.thickness = params.thickness * 0.8

        # Generate using same airfoil logic as wings
        return self._create_stabilizer_wing(h_stab_params)

    def _create_vertical_stabilizer(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Create vertical stabilizer (fin).

        Args:
            params: Base aircraft parameters

        Returns:
            trimesh.Trimesh: Vertical stabilizer mesh (rotated 90 degrees)
        """
        # Scale parameters for vertical stabilizer (50% of main wing)
        v_stab_params = params.model_copy()
        v_stab_params.span = params.span * 0.5  # Becomes height
        v_stab_params.root_chord = params.root_chord * 0.5
        v_stab_params.tip_chord = params.tip_chord * 0.3 if params.tip_chord else params.root_chord * 0.2
        v_stab_params.sweep_angle = params.sweep_angle * 0.8
        v_stab_params.thickness = params.thickness * 0.9
        v_stab_params.dihedral = 0  # No dihedral for vertical stabilizer

        # Create wing-like structure
        vertical_mesh = self._create_stabilizer_wing(v_stab_params)

        # Rotate 90 degrees around X-axis to make it vertical
        rotation_matrix = trimesh.transformations.rotation_matrix(
            np.pi / 2,  # 90 degrees
            [1, 0, 0]   # Around X-axis
        )
        vertical_mesh.apply_transform(rotation_matrix)

        # Position above horizontal stabilizer (T-tail configuration)
        vertical_mesh.vertices[:, 2] += params.span * 0.15

        return vertical_mesh

    def _create_stabilizer_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Create a simple wing-like structure for stabilizers.
        Simplified version of wing generation for tail components.

        Args:
            params: Stabilizer parameters

        Returns:
            trimesh.Trimesh: Stabilizer wing mesh
        """
        half_span = params.span / 2
        root_chord = params.root_chord
        tip_chord = params.tip_chord or 0.1
        thickness_ratio = params.thickness / 100
        sweep_rad = np.radians(params.sweep_angle)
        dihedral_rad = np.radians(params.dihedral)

        # Airfoil profile resolution (lower than main wing for performance)
        num_chord = 15
        num_span = 12

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

            # Generate airfoil profile
            for j in range(num_chord):
                x_chord = j / (num_chord - 1)  # 0 to 1 along chord
                x = x_sweep + x_chord * chord - root_chord / 2

                # Simple airfoil shape
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

        vertices_array = np.array(vertices, dtype=np.float32)

        # Generate faces
        for i in range(num_span - 1):
            for j in range(num_chord - 1):
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

        # Add root edge cap
        for j in range(num_chord - 1):
            upper_curr = j * 2
            lower_curr = j * 2 + 1
            upper_next = (j + 1) * 2
            lower_next = (j + 1) * 2 + 1

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

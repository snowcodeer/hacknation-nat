"""
Wing component generator.
Single Responsibility: Generates only wing geometry.
"""
import numpy as np
import trimesh
from app.models import AeroParameters
from app.services.generators.base_generator import ComponentGenerator


class WingGenerator(ComponentGenerator):
    """
    Generates wing meshes with various configurations (delta, swept, straight, tapered).

    Responsibilities:
    - Generate wing geometry from parameters
    - Support multiple wing types
    - Create flat mounting edge for fuselage attachment
    - Validate wing-specific parameters
    """

    def get_component_type(self) -> str:
        return "wing"

    def validate_parameters(self, params: AeroParameters) -> bool:
        """Validate wing parameters."""
        if params.span <= 0:
            return False
        if params.root_chord <= 0:
            return False
        if params.wing_type not in ['delta', 'swept', 'straight', 'tapered']:
            return False
        return True

    def generate(self, params: AeroParameters) -> trimesh.Trimesh:
        """Generate wing mesh based on wing type."""
        if not self.validate_parameters(params):
            raise ValueError("Invalid wing parameters")

        if params.wing_type == "straight":
            return self._create_straight_wing(params)
        else:
            # Delta, swept, and tapered all use the same base geometry with different params
            return self._create_delta_wing(params)

    def _create_delta_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Create a single wing half (from root to tip) for proper assembly.
        Includes flat mounting edge for fuselage attachment.
        """
        half_span = params.span / 2
        root_chord = params.root_chord
        tip_chord = (params.tip_chord or 0.1)
        thickness_ratio = params.thickness / 100
        sweep_rad = np.radians(params.sweep_angle)
        dihedral_rad = np.radians(params.dihedral)

        # Airfoil profile resolution
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

    def _create_straight_wing(self, params: AeroParameters) -> trimesh.Trimesh:
        """Create a straight wing (no sweep, no taper)."""
        params_copy = params.model_copy()
        params_copy.sweep_angle = 0
        # For truly rectangular wings, tip chord equals root chord
        params_copy.tip_chord = params_copy.root_chord
        return self._create_delta_wing(params_copy)

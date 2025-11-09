"""
Abstract base class for aircraft component generators.
Follows Single Responsibility Principle - each generator handles one component type.
"""
from abc import ABC, abstractmethod
import trimesh
from app.models import AeroParameters


class ComponentGenerator(ABC):
    """
    Abstract base class for all component generators.

    Following SOLID principles:
    - Single Responsibility: Each subclass generates one component type
    - Open/Closed: Open for extension (new generators), closed for modification
    - Liskov Substitution: All generators can be used interchangeably
    - Interface Segregation: Minimal interface with only required methods
    - Dependency Inversion: Depends on AeroParameters abstraction
    """

    @abstractmethod
    def generate(self, params: AeroParameters) -> trimesh.Trimesh:
        """
        Generate 3D mesh for this component type.

        Args:
            params: Component parameters (only uses relevant fields)

        Returns:
            trimesh.Trimesh: Generated 3D mesh
        """
        pass

    @abstractmethod
    def validate_parameters(self, params: AeroParameters) -> bool:
        """
        Validate that parameters are suitable for this component type.

        Args:
            params: Parameters to validate

        Returns:
            bool: True if parameters are valid
        """
        pass

    @abstractmethod
    def get_component_type(self) -> str:
        """
        Get the component type this generator handles.

        Returns:
            str: Component type identifier
        """
        pass

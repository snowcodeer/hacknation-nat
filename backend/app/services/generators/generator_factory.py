"""
Factory for creating component generators.
Implements Factory Pattern for SOLID design.
"""
from typing import Optional
from app.services.generators.base_generator import ComponentGenerator
from app.services.generators.wing_generator import WingGenerator
from app.services.generators.fuselage_generator import FuselageGenerator
from app.services.generators.engine_generator import EngineGenerator


class GeneratorFactory:
    """
    Factory for creating component generators.

    Following SOLID principles:
    - Single Responsibility: Only creates generators
    - Open/Closed: Easy to add new generator types
    - Dependency Inversion: Returns abstract ComponentGenerator type
    """

    # Singleton instances (generators are stateless, can be reused)
    _generators = {
        'wing': WingGenerator(),
        'fuselage': FuselageGenerator(),
        'engine': EngineGenerator()
    }

    @classmethod
    def create(cls, component_type: str) -> Optional[ComponentGenerator]:
        """
        Create a generator for the specified component type.

        Args:
            component_type: Type of component ('wing', 'fuselage', 'engine')

        Returns:
            ComponentGenerator: Generator instance for the component type
            None: If component type is not recognized

        Example:
            generator = GeneratorFactory.create('wing')
            mesh = generator.generate(params)
        """
        component_type_lower = component_type.lower()
        return cls._generators.get(component_type_lower)

    @classmethod
    def get_available_types(cls) -> list[str]:
        """
        Get list of available component types.

        Returns:
            list[str]: List of supported component types
        """
        return list(cls._generators.keys())

    @classmethod
    def register_generator(cls, component_type: str, generator: ComponentGenerator) -> None:
        """
        Register a new generator type (for extensibility).

        Args:
            component_type: Type identifier for the component
            generator: Generator instance to register

        Note:
            This allows plugins or extensions to add new generator types
            without modifying the factory code (Open/Closed Principle)
        """
        cls._generators[component_type.lower()] = generator

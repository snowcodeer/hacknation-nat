import json
from openai import OpenAI
from app.core import settings
from app.models import AeroParameters


class AIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    async def extract_parameters_from_text(self, prompt: str) -> AeroParameters:
        """
        Use GPT-4 to extract structured aerospace parameters from natural language.
        """
        system_prompt = """You are an aerospace engineering expert. Extract precise parametric values from user descriptions of aircraft components.

IMPORTANT: First determine the component type from the prompt:
- If prompt mentions "wing" → generate WING parameters
- If prompt mentions "fuselage" → generate FUSELAGE parameters
- If prompt mentions "tail" or "stabilizer" → generate TAIL parameters
- If prompt mentions "engine" → generate ENGINE parameters

For WINGS:
- wing_type: "delta", "swept", "straight", or "tapered"
- span: number (meters, typically 8-12m for standard aircraft)
- root_chord: number (meters, typically 2-4m)
- tip_chord: number or null (for straight/rectangular wings, tip_chord = root_chord)
- sweep_angle: number (degrees, 0-90)
- thickness: number (10-15)
- dihedral: number (degrees, -10 to 10)
- fuselage_length: null
- fuselage_diameter: null
- engine_length: null
- engine_diameter: null

For FUSELAGE (body/cabin of aircraft):
- wing_type: "straight"
- span: 0.8 (use small value)
- root_chord: same as fuselage_length (for proper alignment)
- tip_chord: root_chord (cylindrical) or 70% of root_chord (tapered)
- sweep_angle: 0
- thickness: 80-100 (fuselage is thick/cylindrical)
- dihedral: 0
- fuselage_type: Determine from prompt keywords:
  * "commercial" / "airliner" / "passenger" / "Boeing" / "Airbus" → "commercial"
  * "fighter" / "jet fighter" / "F-22" / "F-16" / "military" → "fighter"
  * "cargo" / "transport" / "freight" / "C-130" → "cargo"
  * "private" / "business jet" / "Cessna" / "small" → "private"
  * Default: "commercial"
- fuselage_length: actual length from prompt (e.g., 5m → 5m) - realistic dimensions!
- fuselage_diameter: realistic diameter based on type:
  * Commercial: 1.0-1.2m
  * Fighter: 0.5-0.7m (narrow, sleek)
  * Cargo: 1.2-1.5m (wide)
  * Private: 0.6-0.8m (medium)
- engine_length: null
- engine_diameter: null

For TAIL ASSEMBLY (stabilizers at rear):
- wing_type: "swept"
- span: 4-6m (proportional to wing size, about 50-60% of main wing span)
- root_chord: 1.5-2.5m (proportional to wing chord)
- tip_chord: 0.8-1.5m
- sweep_angle: 20-30
- thickness: 10-12
- has_vertical_stabilizer: true
- has_horizontal_stabilizer: true
- fuselage_length: null
- fuselage_diameter: null
- engine_length: null
- engine_diameter: null

For ENGINES (turbine/nacelle):
- wing_type: "straight"
- span: 0.6
- root_chord: same as engine_length (for alignment)
- tip_chord: same as engine_length
- thickness: 90
- fuselage_length: null
- fuselage_diameter: null
- engine_length: actual length (typically 1.5-2.5m for realistic jet engine)
- engine_diameter: actual diameter (typically 0.4-0.6m for realistic jet engine)

ONLY return valid JSON matching these exact field names."""

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            params_dict = json.loads(content)
            print(f"AI extracted parameters: {params_dict}")

            # Convert to Pydantic model for validation
            return AeroParameters(**params_dict)

        except Exception as e:
            print(f"Error extracting parameters: {e}")
            # Return default delta wing on error
            return AeroParameters(
                wing_type="delta",
                span=2.0,
                root_chord=1.0,
                tip_chord=0.2,
                sweep_angle=45,
                thickness=12,
                dihedral=0,
                has_vertical_stabilizer=False,
                has_horizontal_stabilizer=False
            )


    async def generate_complete_aircraft(self, prompt: str) -> dict:
        """
        Use GPT-4 to generate parameters for all 4 components (wings, fuselage, tail, engines)
        from a single natural language description.
        Returns a dict with keys: wings, fuselage, tail_assembly, engines
        """
        system_prompt = """You are an aerospace engineering expert. Generate complete aircraft parameters from natural language descriptions.

The user will describe an aircraft (e.g., "F-22 fighter jet", "Boeing 747", "small private plane").
You must return parameters for ALL 4 components: wings, fuselage, tail_assembly, and engines.

For each component, use the appropriate parameter structure:

WINGS:
- wing_type, span, root_chord, tip_chord, sweep_angle, thickness, dihedral
- has_vertical_stabilizer: false, has_horizontal_stabilizer: false
- All fuselage/engine fields: null

FUSELAGE:
- wing_type: "straight", span: 0.8, thickness: 80-100
- fuselage_type: "commercial"/"fighter"/"cargo"/"private"
- fuselage_length, fuselage_diameter
- All engine fields: null

TAIL_ASSEMBLY:
- wing_type: "swept", span, root_chord, tip_chord, sweep_angle, thickness
- has_vertical_stabilizer: true, has_horizontal_stabilizer: true
- All fuselage/engine fields: null

ENGINES:
- wing_type: "straight", span: 0.6, thickness: 90
- engine_length, engine_diameter
- All fuselage fields: null

Return as JSON with this structure:
{
  "wings": { parameters... },
  "fuselage": { parameters... },
  "tail_assembly": { parameters... },
  "engines": { parameters... }
}"""

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI")

            aircraft_dict = json.loads(content)
            print(f"AI generated complete aircraft: {aircraft_dict}")

            return aircraft_dict

        except Exception as e:
            print(f"Error generating complete aircraft: {e}")
            raise


ai_service = AIService()

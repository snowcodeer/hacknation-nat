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
- span: number (meters, typically 1.5-4m)
- root_chord: number (meters)
- tip_chord: number or null
- sweep_angle: number (degrees, 0-90)
- thickness: number (10-15)
- dihedral: number (degrees, -10 to 10)
- fuselage_length: null
- fuselage_diameter: null

For FUSELAGE:
- wing_type: "straight"
- span: 0.8 (use small value)
- root_chord: use the LENGTH from prompt (e.g., 5m length → root_chord: 5)
- tip_chord: root_chord (cylindrical) or 70% of root_chord (tapered)
- sweep_angle: 0
- thickness: 80-100 (fuselage is thick/cylindrical)
- dihedral: 0
- fuselage_length: number from prompt
- fuselage_diameter: number from prompt

For TAIL ASSEMBLY:
- wing_type: "swept"
- span: 1.5-2m
- sweep_angle: 20-30
- thickness: 10-12
- has_vertical_stabilizer: true
- has_horizontal_stabilizer: true

For ENGINES:
- wing_type: "straight"
- span: 0.6
- root_chord: engine length
- tip_chord: engine length
- thickness: 90
- fuselage_diameter: engine diameter

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


ai_service = AIService()

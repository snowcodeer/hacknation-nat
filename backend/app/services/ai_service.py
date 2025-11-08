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

Return a JSON object with these fields:
- wing_type: "delta", "swept", "straight", or "tapered"
- span: number (meters)
- root_chord: number (meters)
- tip_chord: number or null (meters, for tapered wings)
- sweep_angle: number (degrees, 0-90)
- thickness: number (percentage, 5-20)
- dihedral: number (degrees, -45 to 45)
- has_vertical_stabilizer: boolean
- has_horizontal_stabilizer: boolean

If values aren't specified, use reasonable defaults based on the wing type.
For delta wings: typical sweep 45-50°, span 1.5-3m
For swept wings: typical sweep 25-35°, span 2-4m
For straight wings: sweep 0°, span 2-3m

ONLY return valid JSON, no other text."""

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

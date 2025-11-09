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

IMPORTANT: First determine the component type and AIRCRAFT CLASS from the prompt:

AIRCRAFT CLASSES AND REAL-LIFE DIMENSIONS:
1. COMMERCIAL AIRLINER (Boeing 747, 777, Airbus A380, A320):
   - Wingspan: 35-80m
   - Wing root chord: 12-20m
   - Wing tip chord: 2-5m
   - Fuselage length: 40-75m
   - Fuselage diameter: 5-7m

2. FIGHTER JET (F-22, F-16, F-35, Eurofighter):
   - Wingspan: 10-15m
   - Wing root chord: 6-10m
   - Wing tip chord: 1-3m
   - Fuselage length: 15-20m
   - Fuselage diameter: 1.5-2m

3. CARGO AIRCRAFT (C-130, C-17, An-225):
   - Wingspan: 35-90m
   - Wing root chord: 10-18m
   - Wing tip chord: 3-6m
   - Fuselage length: 35-85m
   - Fuselage diameter: 6-8m

4. PRIVATE/BUSINESS JET (Cessna Citation, Gulfstream):
   - Wingspan: 12-25m
   - Wing root chord: 3-8m
   - Wing tip chord: 1-3m
   - Fuselage length: 12-30m
   - Fuselage diameter: 1.5-2.5m

For WINGS - USE REAL-LIFE SCALE:
- wing_type: "delta", "swept", "straight", or "tapered"
- span: REAL-LIFE wingspan based on aircraft class (see above)
- root_chord: REAL-LIFE root chord based on aircraft class (see above)
- tip_chord: REAL-LIFE tip chord based on aircraft class (see above)
- sweep_angle: number (degrees, 0-90) - Commercial: 25-35°, Fighter: 40-55°, Cargo: 20-30°, Private: 0-25°
- thickness: number (10-15)
- dihedral: number (degrees, -10 to 10)
- fuselage_length: null
- fuselage_diameter: null
- engine_length: null
- engine_diameter: null

For FUSELAGE (body/cabin of aircraft) - USE REAL-LIFE SCALE:
CRITICAL - ALL these fields are REQUIRED:
- wing_type: "straight" (REQUIRED)
- span: 0.8 (REQUIRED - use small value)
- root_chord: same as fuselage_length (REQUIRED for proper alignment)
- tip_chord: root_chord (REQUIRED - cylindrical) or 70% of root_chord (tapered)
- sweep_angle: 0 (REQUIRED)
- thickness: 80-100 (REQUIRED - fuselage is thick/cylindrical)
- dihedral: 0 (REQUIRED)
- fuselage_type: Determine from prompt keywords:
  * "commercial" / "airliner" / "passenger" / "Boeing" / "Airbus" / "747" / "777" / "A320" / "A380" → "commercial"
  * "fighter" / "jet fighter" / "F-22" / "F-16" / "F-35" / "military" → "fighter"
  * "cargo" / "transport" / "freight" / "C-130" / "C-17" → "cargo"
  * "private" / "business jet" / "Cessna" / "Gulfstream" / "Citation" → "private"
  * Default: "commercial"
- fuselage_length: REAL-LIFE length based on aircraft class:
  * Commercial airliner (747, 777, A380): 40-75m
  * Fighter jet (F-22, F-16): 15-20m
  * Cargo (C-130, C-17): 35-85m
  * Private/business: 12-30m
- fuselage_diameter: REAL-LIFE diameter based on aircraft class:
  * Commercial airliner: 5-7m (wide body like 747)
  * Fighter jet: 1.5-2m (narrow, sleek)
  * Cargo: 6-8m (very wide)
  * Private/business: 1.5-2.5m (medium)
- engine_length: null
- engine_diameter: null

For ENGINES (turbine/nacelle) - USE REAL-LIFE SCALE:
CRITICAL - ALL these fields are REQUIRED:
- wing_type: "straight" (REQUIRED)
- span: 0.6 (REQUIRED)
- root_chord: same as engine_length (REQUIRED for alignment)
- tip_chord: same as engine_length (REQUIRED)
- sweep_angle: 0 (REQUIRED)
- thickness: 90 (REQUIRED)
- dihedral: 0 (REQUIRED)
- fuselage_length: null
- fuselage_diameter: null
- engine_length: REAL-LIFE length based on aircraft class:
  * Commercial airliner (GE90, Trent, PW4000): 4-6m
  * Fighter jet (F119, F110): 4-5m
  * Cargo aircraft: 3.5-5m
  * Private/business jet: 2-3.5m
- engine_diameter: REAL-LIFE diameter based on aircraft class:
  * Commercial airliner (high-bypass turbofan): 2.5-3.5m (very large!)
  * Fighter jet (low-bypass): 1-1.5m
  * Cargo aircraft: 2-3m
  * Private/business jet: 0.5-1m

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
            # Return default delta wing on error (much wider chord for better proportions)
            return AeroParameters(
                wing_type="delta",
                span=12.0,
                root_chord=7.0,
                tip_chord=1.5,
                sweep_angle=45,
                thickness=12,
                dihedral=0,
                has_vertical_stabilizer=False,
                has_horizontal_stabilizer=False
            )


    async def generate_complete_aircraft(self, prompt: str) -> dict:
        """
        Use GPT-4 to generate parameters for all 3 components (wings, fuselage, engines)
        from a single natural language description.
        Returns a dict with keys: wings, fuselage, engines
        """
        system_prompt = """You are an aerospace engineering expert. Generate complete aircraft parameters using REAL-LIFE SCALE dimensions.

CRITICAL: Identify the aircraft class first, then use REAL dimensions for that class!

AIRCRAFT CLASSES:
1. COMMERCIAL AIRLINER (747, 777, A380, A320): Wingspan 35-80m, Wing root 12-20m, Fuselage 40-75m × 5-7m
2. FIGHTER JET (F-22, F-16, F-35): Wingspan 10-15m, Wing root 6-10m, Fuselage 15-20m × 1.5-2m
3. CARGO (C-130, C-17, An-225): Wingspan 35-90m, Wing root 10-18m, Fuselage 35-85m × 6-8m
4. PRIVATE/BUSINESS (Cessna, Gulfstream): Wingspan 12-25m, Wing root 3-8m, Fuselage 12-30m × 1.5-2.5m

You must return parameters for ALL 3 components: wings, fuselage, and engines.

WINGS - USE REAL-LIFE SCALE:
- wing_type: "delta", "swept", "straight", or "tapered" (based on aircraft)
- span: REAL wingspan for aircraft class (e.g., 747 = 68m, F-22 = 13.5m)
- root_chord: REAL root chord for aircraft class (e.g., 747 = 15-17m, F-22 = 8m)
- tip_chord: REAL tip chord (e.g., 747 = 2-4m, F-22 = 2m)
- sweep_angle: Typical for aircraft type (Commercial 25-35°, Fighter 40-55°)
- thickness: 10-15
- dihedral: -5 to 10
- has_vertical_stabilizer: false, has_horizontal_stabilizer: false
- All fuselage/engine fields: null

FUSELAGE - USE REAL-LIFE SCALE:
- wing_type: "straight"
- span: 0.8
- root_chord: same as fuselage_length
- tip_chord: same as root_chord
- sweep_angle: 0
- thickness: 80-100
- dihedral: 0
- fuselage_type: "commercial"/"fighter"/"cargo"/"private"
- fuselage_length: REAL length (e.g., 747 = 70m, F-22 = 19m, C-130 = 30m, Cessna = 15m)
- fuselage_diameter: REAL diameter (e.g., 747 = 6.5m, F-22 = 1.8m, C-130 = 3m, Cessna = 1.8m)
- All engine fields: null

ENGINES - USE REAL-LIFE SCALE:
- wing_type: "straight"
- span: 0.6
- root_chord: same as engine_length
- tip_chord: same as engine_length
- sweep_angle: 0
- thickness: 90
- dihedral: 0
- engine_length: REAL length (747 = 5m, F-22 = 5m, C-130 = 4m, Cessna = 2.5m)
- engine_diameter: REAL diameter (747 = 3.2m [GE90], F-22 = 1.2m, C-130 = 2.5m, Cessna = 0.7m)
- All fuselage fields: null

Return as JSON:
{
  "wings": { parameters... },
  "fuselage": { parameters... },
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


    async def calculate_intelligent_assembly(self, components_data: dict) -> dict:
        """
        Use AI to intelligently position aircraft components with proper attachment points,
        interference checking, and realistic positioning.

        Args:
            components_data: Dict with keys 'wings', 'fuselage', 'engines' containing their parameters

        Returns:
            Dict with positioning data for each component
        """
        system_prompt = """You are an aerospace assembly engineer expert. Analyze aircraft components and calculate precise attachment points and positioning.

Your task: Given component dimensions, calculate realistic positioning that ensures:
1. Proper structural attachment points
2. No interference between components
3. Aerodynamically sound positioning
4. Center of gravity balance
5. Real-world engineering practices

Return precise positioning data as JSON."""

        # Extract component parameters for AI analysis
        wings_params = components_data.get('wings', {}).get('parameters', {})
        fuselage_params = components_data.get('fuselage', {}).get('parameters', {})
        engines_params = components_data.get('engines', {}).get('parameters', {})

        user_prompt = f"""Analyze these aircraft components and calculate optimal assembly positioning:

WINGS:
- Wingspan: {wings_params.get('span', 0)}m
- Root chord: {wings_params.get('root_chord', 0)}m
- Tip chord: {wings_params.get('tip_chord', 0)}m
- Sweep angle: {wings_params.get('sweep_angle', 0)}°
- Wing type: {wings_params.get('wing_type', 'unknown')}

FUSELAGE:
- Length: {fuselage_params.get('fuselage_length', 0)}m
- Diameter: {fuselage_params.get('fuselage_diameter', 0)}m
- Type: {fuselage_params.get('fuselage_type', 'unknown')}

ENGINES:
- Length: {engines_params.get('engine_length', 0)}m
- Diameter: {engines_params.get('engine_diameter', 0)}m

Calculate positioning for:
1. WING_POSITION_X: Distance from fuselage nose where wings attach (typically 30-40% of fuselage length for balance)
2. ENGINE_POSITION_Y: Distance from fuselage centerline (typically 30-45% of wing semi-span)
3. ENGINE_POSITION_Z: Height below wing lower surface (engines hang below wings)

Return JSON with this exact structure:
{{
  "wing_attachment": {{
    "position_x": <meters from nose, negative for aft>,
    "position_y": 0,
    "position_z": <meters, typically near fuselage centerline>,
    "reasoning": "why this position for aerodynamics and balance"
  }},
  "engine_attachment": {{
    "position_x": <meters, align with or slightly forward of wing attachment>,
    "position_y": <meters from centerline, 30-45% of wing semi-span>,
    "position_z": <meters below wing, negative value>,
    "reasoning": "why this position for ground clearance and wing stress distribution"
  }},
  "interference_check": {{
    "wings_fuselage": "clear|interference",
    "engines_fuselage": "clear|interference",
    "engines_ground": "adequate_clearance|too_low",
    "notes": "any warnings or adjustments needed"
  }},
  "center_of_gravity": {{
    "estimated_x": <meters from nose>,
    "within_limits": true|false,
    "recommendation": "any adjustments needed for balance"
  }}
}}"""

        try:
            response = self.client.chat.completions.create(
                model=settings.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.2,  # Low temperature for precise calculations
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            if not content:
                raise ValueError("Empty response from OpenAI for assembly calculation")

            assembly_data = json.loads(content)
            print(f"AI calculated assembly positioning: {assembly_data}")

            return assembly_data

        except Exception as e:
            print(f"Error calculating intelligent assembly: {e}")
            # Fallback to safe default positioning
            return {
                "wing_attachment": {
                    "position_x": 0,
                    "position_y": 0,
                    "position_z": 0,
                    "reasoning": "fallback default positioning"
                },
                "engine_attachment": {
                    "position_x": 0,
                    "position_y": 5.0,
                    "position_z": -1.5,
                    "reasoning": "fallback default positioning"
                },
                "interference_check": {
                    "wings_fuselage": "unknown",
                    "engines_fuselage": "unknown",
                    "engines_ground": "unknown",
                    "notes": "using fallback positioning due to AI error"
                },
                "center_of_gravity": {
                    "estimated_x": 0,
                    "within_limits": True,
                    "recommendation": "manual verification recommended"
                }
            }


ai_service = AIService()

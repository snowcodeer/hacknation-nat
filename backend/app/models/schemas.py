from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime
import uuid


class AeroParameters(BaseModel):
    """Parametric definition of aerospace component"""
    wing_type: Literal['delta', 'swept', 'straight', 'tapered']
    span: float = Field(gt=0, description="Wing span in meters")
    root_chord: float = Field(gt=0, description="Root chord length in meters")
    tip_chord: Optional[float] = Field(None, gt=0, description="Tip chord length in meters")
    sweep_angle: float = Field(ge=0, le=90, description="Sweep angle in degrees")
    thickness: float = Field(gt=0, le=100, description="Thickness as percentage")
    dihedral: float = Field(ge=-45, le=45, description="Dihedral angle in degrees")

    fuselage_length: Optional[float] = None
    fuselage_diameter: Optional[float] = None

    has_vertical_stabilizer: bool = False
    has_horizontal_stabilizer: bool = False


class GeometryData(BaseModel):
    """3D geometry data"""
    vertices: list[float]
    indices: list[int]
    normals: Optional[list[float]] = None


class ModelMetadata(BaseModel):
    """Model metadata"""
    created_at: datetime
    updated_at: datetime
    generated_from: Literal['text', 'image', 'manual']
    source_prompt: Optional[str] = None


class Model3D(BaseModel):
    """Complete 3D model"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    parameters: AeroParameters
    geometry: GeometryData
    metadata: ModelMetadata


class GenerateRequest(BaseModel):
    """Request to generate model from text"""
    prompt: str = Field(min_length=1, description="Text description of aerospace component")


class UpdateParametersRequest(BaseModel):
    """Request to update model parameters"""
    parameters: AeroParameters


class GenerateResponse(BaseModel):
    """Response from generation"""
    success: bool
    model: Optional[Model3D] = None
    parameters: Optional[AeroParameters] = None
    error: Optional[str] = None


class ExportOptions(BaseModel):
    """Export options"""
    binary: Optional[bool] = True  # STL only
    units: Optional[Literal['mm', 'm', 'in']] = 'm'


class ExportRequest(BaseModel):
    """Request to export model"""
    model_id: str
    options: Optional[ExportOptions] = None


class ImageUploadResponse(BaseModel):
    """Response from image upload"""
    success: bool
    url: Optional[str] = None
    error: Optional[str] = None

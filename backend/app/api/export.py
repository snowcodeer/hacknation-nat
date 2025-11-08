from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from app.models import ExportRequest
from app.services import export_service
from app.api.generation import current_model

router = APIRouter(prefix="/export", tags=["export"])


@router.post("/stl")
async def export_stl(request: ExportRequest):
    """
    Export model as STL file.
    """
    # In production, retrieve model from database
    if current_model is None or current_model.id != request.model_id:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        stl_data = export_service.export_stl(current_model, request.options)

        return Response(
            content=stl_data,
            media_type="application/sla",
            headers={
                "Content-Disposition": f"attachment; filename={current_model.name}.stl"
            }
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/step")
async def export_step(request: ExportRequest):
    """
    Export model as STEP file.
    Note: Requires pythonOCC - currently not implemented.
    """
    if current_model is None or current_model.id != request.model_id:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        step_data = export_service.export_step(current_model, request.options)

        return Response(
            content=step_data,
            media_type="application/step",
            headers={
                "Content-Disposition": f"attachment; filename={current_model.name}.step"
            }
        )

    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/iges")
async def export_iges(request: ExportRequest):
    """
    Export model as IGES file.
    Note: Requires pythonOCC - currently not implemented.
    """
    if current_model is None or current_model.id != request.model_id:
        raise HTTPException(status_code=404, detail="Model not found")

    try:
        iges_data = export_service.export_iges(current_model, request.options)

        return Response(
            content=iges_data,
            media_type="application/iges",
            headers={
                "Content-Disposition": f"attachment; filename={current_model.name}.iges"
            }
        )

    except NotImplementedError as e:
        raise HTTPException(status_code=501, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

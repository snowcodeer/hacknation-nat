import trimesh
import numpy as np
from io import BytesIO
from app.models import Model3D, ExportOptions


class ExportService:
    def export_stl(self, model: Model3D, options: ExportOptions = None) -> bytes:
        """
        Export model to STL format (binary or ASCII).
        """
        options = options or ExportOptions()

        # Reconstruct trimesh from model geometry
        vertices = np.array(model.geometry.vertices).reshape(-1, 3)
        faces = np.array(model.geometry.indices).reshape(-1, 3)

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        # Export to BytesIO
        output = BytesIO()
        mesh.export(output, file_type='stl', file_obj=output)
        output.seek(0)

        return output.getvalue()

    def export_step(self, model: Model3D, options: ExportOptions = None) -> bytes:
        """
        Export model to STEP format.
        Note: This requires pythonOCC which is complex to install.
        For MVP, we'll return a placeholder or convert via intermediate format.
        """
        # TODO: Implement STEP export with pythonOCC
        # For now, we'll raise an error or return STL as fallback
        raise NotImplementedError(
            "STEP export requires pythonOCC installation. "
            "Please use STL export for now."
        )

    def export_iges(self, model: Model3D, options: ExportOptions = None) -> bytes:
        """
        Export model to IGES format.
        Note: This also requires pythonOCC.
        """
        # TODO: Implement IGES export with pythonOCC
        raise NotImplementedError(
            "IGES export requires pythonOCC installation. "
            "Please use STL export for now."
        )

    def export_obj(self, model: Model3D) -> bytes:
        """
        Export model to OBJ format (additional format).
        """
        vertices = np.array(model.geometry.vertices).reshape(-1, 3)
        faces = np.array(model.geometry.indices).reshape(-1, 3)

        mesh = trimesh.Trimesh(vertices=vertices, faces=faces)

        output = BytesIO()
        mesh.export(output, file_type='obj', file_obj=output)
        output.seek(0)

        return output.getvalue()


export_service = ExportService()

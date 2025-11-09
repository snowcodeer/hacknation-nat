import type { GenerateResponse, AeroParameters, ExportFormat, Model3D } from '$lib/types/model';

const API_BASE = '/api';

// Helper function to convert backend snake_case to frontend camelCase
function mapBackendToFrontend(backendData: any): Model3D {
	return {
		id: backendData.id,
		name: backendData.name,
		parameters: {
			wingType: backendData.parameters.wing_type,
			span: backendData.parameters.span,
			rootChord: backendData.parameters.root_chord,
			tipChord: backendData.parameters.tip_chord,
			sweepAngle: backendData.parameters.sweep_angle,
			thickness: backendData.parameters.thickness,
			dihedral: backendData.parameters.dihedral,
			fuselageType: backendData.parameters.fuselage_type,
			fuselageLength: backendData.parameters.fuselage_length,
			fuselageDiameter: backendData.parameters.fuselage_diameter,
			engineLength: backendData.parameters.engine_length,
			engineDiameter: backendData.parameters.engine_diameter,
			hasVerticalStabilizer: backendData.parameters.has_vertical_stabilizer,
			hasHorizontalStabilizer: backendData.parameters.has_horizontal_stabilizer,
			positionX: backendData.parameters.position_x,
			positionY: backendData.parameters.position_y,
			positionZ: backendData.parameters.position_z
		},
		geometry: {
			// Convert arrays to Typed Arrays
			vertices: backendData.geometry.vertices instanceof Float32Array 
				? backendData.geometry.vertices 
				: new Float32Array(backendData.geometry.vertices),
			indices: backendData.geometry.indices instanceof Uint32Array 
				? backendData.geometry.indices 
				: new Uint32Array(backendData.geometry.indices),
			normals: backendData.geometry.normals 
				? (backendData.geometry.normals instanceof Float32Array 
					? backendData.geometry.normals 
					: new Float32Array(backendData.geometry.normals))
				: undefined
		},
		metadata: {
			createdAt: new Date(),
			updatedAt: new Date(),
			generatedFrom: 'text'
		}
	};
}

// Helper function to convert frontend camelCase to backend snake_case
function mapFrontendToBackend(parameters: AeroParameters): any {
	return {
		// Required fields - always include with fallback defaults
		wing_type: parameters.wingType || 'straight',
		span: parameters.span ?? 1.0,
		root_chord: parameters.rootChord ?? 1.0,
		tip_chord: parameters.tipChord ?? parameters.rootChord ?? 1.0,
		sweep_angle: parameters.sweepAngle ?? 0,
		thickness: parameters.thickness ?? 12,
		dihedral: parameters.dihedral ?? 0,
		// Optional fields - send as-is (can be null/undefined)
		fuselage_type: parameters.fuselageType,
		fuselage_length: parameters.fuselageLength,
		fuselage_diameter: parameters.fuselageDiameter,
		engine_length: parameters.engineLength,
		engine_diameter: parameters.engineDiameter,
		has_vertical_stabilizer: parameters.hasVerticalStabilizer || false,
		has_horizontal_stabilizer: parameters.hasHorizontalStabilizer || false,
		position_x: parameters.positionX || 0,
		position_y: parameters.positionY || 0,
		position_z: parameters.positionZ || 0
	};
}

class ApiService {
	async generateFromText(prompt: string): Promise<GenerateResponse> {
		try {
			const response = await fetch(`${API_BASE}/generate/from-text`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ prompt })
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			
			if (data.success && data.model) {
				return {
					success: true,
					model: mapBackendToFrontend(data.model)
				};
			}
			
			return data;
		} catch (error) {
			console.error('Error generating from text:', error);
			return {
				success: false,
				error: error instanceof Error ? error.message : 'Unknown error'
			};
		}
	}

	async updateParameters(parameters: AeroParameters): Promise<GenerateResponse> {
		try {
			const backendParams = mapFrontendToBackend(parameters);
			
			const response = await fetch(`${API_BASE}/generate/update-parameters`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ parameters: backendParams })
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();
			
			if (data.success && data.model) {
				return {
					success: true,
					model: mapBackendToFrontend(data.model)
				};
			}
			
			return data;
		} catch (error) {
			console.error('Error updating parameters:', error);
			return {
				success: false,
				error: error instanceof Error ? error.message : 'Unknown error'
			};
		}
	}

	async uploadReferenceImage(file: File): Promise<{ success: boolean; url?: string; error?: string }> {
		try {
			const formData = new FormData();
			formData.append('file', file);

			const response = await fetch(`${API_BASE}/images/upload`, {
				method: 'POST',
				body: formData
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			return await response.json();
		} catch (error) {
			console.error('Error uploading image:', error);
			return {
				success: false,
				error: error instanceof Error ? error.message : 'Unknown error'
			};
		}
	}

	async exportModel(modelId: string, exportFormat: ExportFormat): Promise<Blob> {
		const response = await fetch(`${API_BASE}/export/${exportFormat.format}`, {
			method: 'POST',
			headers: { 'Content-Type': 'application/json' },
			body: JSON.stringify({
				modelId,
				options: exportFormat.options
			})
		});

		if (!response.ok) {
			throw new Error(`Export failed: ${response.status}`);
		}

		return await response.blob();
	}

	async compileAircraft(aircraft: any): Promise<GenerateResponse> {
		try {
			const response = await fetch(`${API_BASE}/generate/compile-aircraft`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ aircraft })
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();

			if (data.success && data.model) {
				return {
					success: true,
					model: mapBackendToFrontend(data.model)
				};
			}

			return data;
		} catch (error) {
			console.error('Error compiling aircraft:', error);
			return {
				success: false,
				error: error instanceof Error ? error.message : 'Unknown error'
			};
		}
	}
}

export const apiService = new ApiService();

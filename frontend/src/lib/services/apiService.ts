import type { GenerateResponse, AeroParameters, ExportFormat, Model3D } from '$lib/types/model';

const API_BASE = '/api';

// Helper function to convert backend snake_case to frontend camelCase
function mapBackendToFrontend(backendData: any): Model3D {
	const params = backendData.parameters || {};
	return {
		id: backendData.id,
		name: backendData.name,
		parameters: {
			wingType: params.wing_type ?? 'straight',
			span: params.span ?? 1.0,
			rootChord: params.root_chord ?? 1.0,
			tipChord: params.tip_chord ?? params.root_chord ?? 1.0,
			sweepAngle: params.sweep_angle ?? 0,
			thickness: params.thickness ?? 12,
			dihedral: params.dihedral ?? 0,
			fuselageType: params.fuselage_type,
			fuselageLength: params.fuselage_length,
			fuselageDiameter: params.fuselage_diameter,
			engineLength: params.engine_length,
			engineDiameter: params.engine_diameter,
			hasVerticalStabilizer: params.has_vertical_stabilizer ?? false,
			hasHorizontalStabilizer: params.has_horizontal_stabilizer ?? false,
			positionX: params.position_x ?? 0,
			positionY: params.position_y ?? 0,
			positionZ: params.position_z ?? 0
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

	async editComponent(prompt: string, aircraft: any): Promise<{
		success: boolean;
		component?: string;
		operation?: string;
		description?: string;
		model?: Model3D;
		parameters?: AeroParameters;
		error?: string;
	}> {
		try {
			const response = await fetch(`${API_BASE}/generate/edit-component`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ prompt, aircraft })
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			const data = await response.json();

			if (data.success && data.model) {
				return {
					success: true,
					component: data.component,
					operation: data.operation,
					description: data.description,
					model: mapBackendToFrontend(data.model),
					parameters: {
						wingType: data.parameters.wing_type ?? 'straight',
						span: data.parameters.span ?? 1.0,
						rootChord: data.parameters.root_chord ?? 1.0,
						tipChord: data.parameters.tip_chord ?? data.parameters.root_chord ?? 1.0,
						sweepAngle: data.parameters.sweep_angle ?? 0,
						thickness: data.parameters.thickness ?? 12,
						dihedral: data.parameters.dihedral ?? 0,
						fuselageType: data.parameters.fuselage_type,
						fuselageLength: data.parameters.fuselage_length,
						fuselageDiameter: data.parameters.fuselage_diameter,
						engineLength: data.parameters.engine_length,
						engineDiameter: data.parameters.engine_diameter,
						hasVerticalStabilizer: data.parameters.has_vertical_stabilizer ?? false,
						hasHorizontalStabilizer: data.parameters.has_horizontal_stabilizer ?? false,
						positionX: data.parameters.position_x ?? 0,
						positionY: data.parameters.position_y ?? 0,
						positionZ: data.parameters.position_z ?? 0
					}
				};
			}

			return data;
		} catch (error) {
			console.error('Error editing component:', error);
			return {
				success: false,
				error: error instanceof Error ? error.message : 'Unknown error'
			};
		}
	}
}

export const apiService = new ApiService();

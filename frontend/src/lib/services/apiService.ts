import type { GenerateRequest, GenerateResponse, AeroParameters, ExportFormat } from '$lib/types/model';

const API_BASE = '/api';

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

			return await response.json();
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
			const response = await fetch(`${API_BASE}/generate/update-parameters`, {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({ parameters })
			});

			if (!response.ok) {
				throw new Error(`HTTP error! status: ${response.status}`);
			}

			return await response.json();
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
}

export const apiService = new ApiService();

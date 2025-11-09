export interface AeroParameters {
	// Wing parameters
	wingType: 'delta' | 'swept' | 'straight' | 'tapered';
	span: number;           // meters
	rootChord: number;      // meters
	tipChord?: number;      // meters (for tapered wings)
	sweepAngle: number;     // degrees
	thickness: number;      // percentage (10 = 10%)
	dihedral: number;       // degrees

	// Fuselage parameters (ONLY for fuselage component)
	fuselageLength?: number;
	fuselageDiameter?: number;

	// Engine parameters (ONLY for engine component)
	engineLength?: number;
	engineDiameter?: number;

	// Other components
	hasVerticalStabilizer: boolean;
	hasHorizontalStabilizer: boolean;
}

export interface Model3D {
	id: string;
	name: string;
	parameters: AeroParameters;
	geometry: {
		vertices: Float32Array;
		indices: Uint32Array;
		normals?: Float32Array;
	};
	metadata: {
		createdAt: Date;
		updatedAt: Date;
		generatedFrom: 'text' | 'image' | 'manual';
		sourcePrompt?: string;
	};
}

export interface GenerateRequest {
	prompt: string;
	imageUrl?: string;
}

export interface GenerateResponse {
	success: boolean;
	model?: Model3D;
	parameters?: AeroParameters;
	error?: string;
}

export interface ExportFormat {
	format: 'stl' | 'step' | 'iges';
	options?: {
		binary?: boolean;  // STL only
		units?: 'mm' | 'm' | 'in';
	};
}

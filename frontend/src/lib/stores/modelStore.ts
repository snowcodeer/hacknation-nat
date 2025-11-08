import { writable, derived } from 'svelte/store';
import type { Model3D, AeroParameters } from '$lib/types/model';

// Default parameters for a simple delta wing
const defaultParameters: AeroParameters = {
	wingType: 'delta',
	span: 2.0,
	rootChord: 1.0,
	tipChord: 0.2,
	sweepAngle: 45,
	thickness: 12,
	dihedral: 0,
	hasVerticalStabilizer: false,
	hasHorizontalStabilizer: false
};

// Current model state
export const currentModel = writable<Model3D | null>(null);

// Current parameters (can be edited independently before regenerating)
export const parameters = writable<AeroParameters>(defaultParameters);

// Loading state
export const isGenerating = writable<boolean>(false);

// Error state
export const generationError = writable<string | null>(null);

// Derived store: whether we have a valid model
export const hasModel = derived(currentModel, ($model) => $model !== null);

// Reference image
export const referenceImage = writable<string | null>(null);

// Helper functions
export function updateParameter<K extends keyof AeroParameters>(
	key: K,
	value: AeroParameters[K]
) {
	parameters.update((p) => ({ ...p, [key]: value }));
}

export function resetParameters() {
	parameters.set(defaultParameters);
}

export function setModel(model: Model3D) {
	currentModel.set(model);
	parameters.set(model.parameters);
	generationError.set(null);
}

export function clearModel() {
	currentModel.set(null);
	generationError.set(null);
}

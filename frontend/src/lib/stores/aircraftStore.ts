import { writable, derived } from 'svelte/store';
import type { Model3D } from '$lib/types/model';

export type ComponentType = 'wing' | 'fuselage' | 'vertical_stabilizer' | 'horizontal_stabilizer';

export interface AircraftComponent {
	type: ComponentType;
	model: Model3D | null;
	isGenerating: boolean;
	error: string | null;
}

export interface Aircraft {
	wing: AircraftComponent;
	fuselage: AircraftComponent;
	verticalStabilizer: AircraftComponent;
	horizontalStabilizer: AircraftComponent;
}

const initialAircraft: Aircraft = {
	wing: { type: 'wing', model: null, isGenerating: false, error: null },
	fuselage: { type: 'fuselage', model: null, isGenerating: false, error: null },
	verticalStabilizer: { type: 'vertical_stabilizer', model: null, isGenerating: false, error: null },
	horizontalStabilizer: { type: 'horizontal_stabilizer', model: null, isGenerating: false, error: null }
};

// Main aircraft store
export const aircraft = writable<Aircraft>(initialAircraft);

// Current active component being edited
export const activeComponent = writable<ComponentType>('wing');

// Derived: completion status
export const completionStatus = derived(aircraft, ($aircraft) => ({
	wing: $aircraft.wing.model !== null,
	fuselage: $aircraft.fuselage.model !== null,
	verticalStabilizer: $aircraft.verticalStabilizer.model !== null,
	horizontalStabilizer: $aircraft.horizontalStabilizer.model !== null
}));

// Derived: is assembly ready (at least wing is complete)
export const isAssemblyReady = derived(completionStatus, ($status) => $status.wing);

// Derived: all components for 3D viewer
export const allComponents = derived(aircraft, ($aircraft) => {
	const components: Model3D[] = [];
	if ($aircraft.wing.model) components.push($aircraft.wing.model);
	if ($aircraft.fuselage.model) components.push($aircraft.fuselage.model);
	if ($aircraft.verticalStabilizer.model) components.push($aircraft.verticalStabilizer.model);
	if ($aircraft.horizontalStabilizer.model) components.push($aircraft.horizontalStabilizer.model);
	return components;
});

// Helper functions
export function setComponentModel(componentType: ComponentType, model: Model3D) {
	aircraft.update(state => ({
		...state,
		[componentType]: {
			...state[componentType],
			model,
			isGenerating: false,
			error: null
		}
	}));
}

export function setComponentGenerating(componentType: ComponentType, isGenerating: boolean) {
	aircraft.update(state => ({
		...state,
		[componentType]: {
			...state[componentType],
			isGenerating
		}
	}));
}

export function setComponentError(componentType: ComponentType, error: string) {
	aircraft.update(state => ({
		...state,
		[componentType]: {
			...state[componentType],
			error,
			isGenerating: false
		}
	}));
}

export function clearComponent(componentType: ComponentType) {
	aircraft.update(state => ({
		...state,
		[componentType]: {
			...state[componentType],
			model: null,
			error: null
		}
	}));
}

export function resetAircraft() {
	aircraft.set(initialAircraft);
	activeComponent.set('wing');
}

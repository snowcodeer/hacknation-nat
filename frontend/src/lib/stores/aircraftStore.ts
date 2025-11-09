import { writable, derived } from 'svelte/store';
import type { Model3D } from '$lib/types/model';

export type ComponentType = 'wings' | 'fuselage' | 'engines';

export interface AircraftComponent {
	type: ComponentType;
	model: Model3D | null;
	isGenerating: boolean;
	error: string | null;
}

export interface Aircraft {
	wings: AircraftComponent;
	fuselage: AircraftComponent;
	engines: AircraftComponent;
}

const initialAircraft: Aircraft = {
	wings: { type: 'wings', model: null, isGenerating: false, error: null },
	fuselage: { type: 'fuselage', model: null, isGenerating: false, error: null },
	engines: { type: 'engines', model: null, isGenerating: false, error: null }
};

// Main aircraft store
export const aircraft = writable<Aircraft>(initialAircraft);

// Current active component being edited
export const activeComponent = writable<ComponentType>('wings');

// Compiled aircraft model (all components merged into one)
export const compiledAircraft = writable<Model3D | null>(null);

// Compilation status
export const isCompiling = writable<boolean>(false);

// Derived: completion status
export const completionStatus = derived(aircraft, ($aircraft) => ({
	wings: $aircraft.wings.model !== null,
	fuselage: $aircraft.fuselage.model !== null,
	engines: $aircraft.engines.model !== null
}));

// Derived: is assembly ready (at least wings is complete)
export const isAssemblyReady = derived(completionStatus, ($status) => $status.wings);

// Derived: all components complete (ready to compile)
export const allComponentsComplete = derived(completionStatus, ($status) =>
	$status.wings && $status.fuselage && $status.engines
);

// Derived: all components for 3D viewer
export const allComponents = derived(aircraft, ($aircraft) => {
	const components: Model3D[] = [];
	if ($aircraft.wings.model) components.push($aircraft.wings.model);
	if ($aircraft.fuselage.model) components.push($aircraft.fuselage.model);
	if ($aircraft.engines.model) components.push($aircraft.engines.model);
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
	activeComponent.set('wings');
	compiledAircraft.set(null);
}

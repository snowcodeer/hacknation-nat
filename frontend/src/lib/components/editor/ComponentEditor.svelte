<script lang="ts">
	import { apiService } from '$lib/services/apiService';
	import {
		aircraft,
		setComponentModel,
		setComponentGenerating,
		setComponentError,
		type ComponentType
	} from '$lib/stores/aircraftStore';
	import type { ComponentType as CT } from '$lib/stores/aircraftStore';

	export let componentType: CT;

	let prompt = '';
	let previousComponentType: CT = componentType;

	// Reset prompt when component type changes
	$: if (componentType !== previousComponentType) {
		prompt = '';
		previousComponentType = componentType;
	}

	$: component = $aircraft[componentType];
	$: isGenerating = component?.isGenerating || false;
	$: error = component?.error || null;
	$: model = component?.model || null;

	const componentPrompts: Record<CT, string[]> = {
		wings: [
			'Delta wing with 45° sweep, 2m span',
			'Straight wing, 3m span, rectangular',
			'Swept wing with 30° sweep, 2.5m span'
		],
		fuselage: [
			'Cylindrical fuselage, 5m length, 1.2m diameter',
			'Tapered fuselage, 6m length, streamlined',
			'Wide body fuselage, 8m length, 2m diameter'
		],
		tail_assembly: [
			'Swept tail assembly, 2m span with vertical stabilizer',
			'T-tail configuration, 1.8m horizontal span',
			'Conventional tail with rudder and elevator'
		],
		engines: [
			'Twin jet engines, 1.5m length, 0.8m diameter each',
			'Single turboprop engine, 2m length, 1m diameter',
			'Four turbofan engines, 1.2m length each'
		]
	};

	async function handleGenerate() {
		if (!prompt.trim()) return;

		console.log('Generating component:', componentType, 'with prompt:', prompt);
		setComponentGenerating(componentType, true);

		// Prepend component type to prompt for better AI understanding
		const componentName = componentType.replace('_', ' ');
		const enhancedPrompt = `Generate aircraft ${componentName}: ${prompt}`;

		const response = await apiService.generateFromText(enhancedPrompt);

		if (response.success && response.model) {
			console.log('Generated successfully:', response.model.name);
			setComponentModel(componentType, response.model);
		} else {
			console.error('Generation failed:', response.error);
			setComponentError(componentType, response.error || 'Failed to generate');
		}
	}

	function useExample(example: string) {
		prompt = example;
	}
</script>

<div class="component-editor">
	<div class="prompt-section">
		<label for="prompt">Describe this component</label>
		<textarea
			id="prompt"
			bind:value={prompt}
			placeholder="Describe the {componentType.replace('_', ' ')}..."
			rows="4"
			disabled={isGenerating}
		/>

		<button
			class="generate-btn"
			on:click={handleGenerate}
			disabled={isGenerating || !prompt.trim()}
		>
			{isGenerating ? 'Generating...' : 'Generate Component'}
		</button>

		{#if error}
			<div class="error-message">
				{error}
			</div>
		{/if}
	</div>

	<div class="examples-section">
		<h3>Quick Start Examples</h3>
		<div class="examples-grid">
			{#each componentPrompts[componentType] as example}
				<button
					class="example-btn"
					on:click={() => useExample(example)}
					disabled={isGenerating}
				>
					{example}
				</button>
			{/each}
		</div>
	</div>

	{#if model}
		<div class="component-info">
			<h3>✓ Component Generated</h3>
			<p class="component-name">{model.name}</p>
			<p class="component-detail">Ready for assembly</p>
		</div>
	{/if}
</div>

<style>
	.component-editor {
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.prompt-section {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	label {
		font-size: 0.875rem;
		font-weight: 600;
		color: #f1f5f9;
	}

	textarea {
		max-width: 700px;
		width: 100%;
		min-width: 300px;
		padding: 0.875rem;
		background: #1e293b;
		border: 2px solid #334155;
		border-radius: 0.5rem;
		color: #f1f5f9;
		font-size: 0.875rem;
		resize: both;
		font-family: inherit;
		transition: border-color 0.2s;
	}

	textarea:focus {
		outline: none;
		border-color: #3b82f6;
	}

	textarea::placeholder {
		color: #64748b;
	}

	.generate-btn {
		padding: 0.875rem 1.5rem;
		background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
		color: white;
		border: none;
		border-radius: 0.5rem;
		font-weight: 600;
		font-size: 0.875rem;
		cursor: pointer;
		transition: all 0.2s;
	}

	.generate-btn:not(:disabled):hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 16px rgba(59, 130, 246, 0.3);
	}

	.generate-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
		transform: none;
	}

	.error-message {
		padding: 0.875rem;
		background: rgba(239, 68, 68, 0.1);
		border: 2px solid #ef4444;
		border-radius: 0.5rem;
		color: #fca5a5;
		font-size: 0.875rem;
	}

	.examples-section h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: #94a3b8;
		margin: 0 0 1rem;
	}

	.examples-grid {
		display: grid;
		gap: 0.75rem;
	}

	.example-btn {
		padding: 0.875rem;
		background: #1e293b;
		border: 2px solid #334155;
		border-radius: 0.5rem;
		color: #cbd5e1;
		font-size: 0.8125rem;
		text-align: left;
		cursor: pointer;
		transition: all 0.2s;
	}

	.example-btn:not(:disabled):hover {
		border-color: #3b82f6;
		color: #f1f5f9;
		transform: translateX(4px);
	}

	.example-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.component-info {
		padding: 1.5rem;
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		border-radius: 0.75rem;
		color: white;
	}

	.component-info h3 {
		margin: 0;
		font-size: 1rem;
		font-weight: 600;
	}

	.component-name {
		margin: 0.5rem 0 0.25rem;
		font-size: 1.125rem;
		font-weight: 700;
	}

	.component-detail {
		margin: 0;
		font-size: 0.875rem;
		opacity: 0.9;
	}
</style>

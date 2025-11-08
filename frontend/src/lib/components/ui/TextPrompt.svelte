<script lang="ts">
	import { apiService } from '$lib/services/apiService';
	import { isGenerating, generationError, setModel } from '$lib/stores/modelStore';

	let prompt = '';

	async function handleGenerate() {
		if (!prompt.trim()) return;

		$isGenerating = true;
		$generationError = null;

		const response = await apiService.generateFromText(prompt);

		if (response.success && response.model) {
			setModel(response.model);
		} else {
			$generationError = response.error || 'Failed to generate model';
		}

		$isGenerating = false;
	}

	const examples = [
		'Delta wing with 45° sweep, 2m span',
		'Straight wing aircraft, 3m span, 0.5m chord',
		'Swept wing with vertical stabilizer',
		'Tapered wing, 2.5m span, 30° sweep'
	];

	function useExample(example: string) {
		prompt = example;
	}
</script>

<div class="text-prompt">
	<textarea
		bind:value={prompt}
		placeholder="Describe your aerospace component..."
		rows="4"
		disabled={$isGenerating}
	/>

	<button
		class="generate-btn"
		on:click={handleGenerate}
		disabled={$isGenerating || !prompt.trim()}
	>
		{$isGenerating ? 'Generating...' : 'Generate 3D Model'}
	</button>

	{#if $generationError}
		<div class="error-message">
			{$generationError}
		</div>
	{/if}

	<div class="examples">
		<p class="examples-label">Examples:</p>
		{#each examples as example}
			<button
				class="example-btn"
				on:click={() => useExample(example)}
				disabled={$isGenerating}
			>
				{example}
			</button>
		{/each}
	</div>
</div>

<style>
	.text-prompt {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	textarea {
		width: 100%;
		padding: 0.75rem;
		background: var(--bg-tertiary);
		border: 1px solid var(--border-color);
		border-radius: 0.375rem;
		color: var(--text-primary);
		font-size: 0.875rem;
		resize: vertical;
		min-height: 80px;
	}

	textarea:focus {
		outline: none;
		border-color: var(--accent-primary);
	}

	textarea::placeholder {
		color: var(--text-secondary);
	}

	.generate-btn {
		padding: 0.75rem 1rem;
		background: var(--accent-primary);
		color: white;
		border: none;
		border-radius: 0.375rem;
		font-weight: 600;
		font-size: 0.875rem;
		transition: background 0.2s;
	}

	.generate-btn:hover:not(:disabled) {
		background: var(--accent-hover);
	}

	.generate-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.error-message {
		padding: 0.75rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid var(--error);
		border-radius: 0.375rem;
		color: var(--error);
		font-size: 0.875rem;
	}

	.examples {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.examples-label {
		font-size: 0.75rem;
		color: var(--text-secondary);
		margin: 0;
	}

	.example-btn {
		padding: 0.5rem;
		background: var(--bg-tertiary);
		border: 1px solid var(--border-color);
		border-radius: 0.25rem;
		color: var(--text-secondary);
		font-size: 0.75rem;
		text-align: left;
		transition: all 0.2s;
	}

	.example-btn:hover:not(:disabled) {
		background: var(--bg-primary);
		border-color: var(--accent-primary);
		color: var(--text-primary);
	}

	.example-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>

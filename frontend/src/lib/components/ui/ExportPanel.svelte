<script lang="ts">
	import { currentModel, hasModel } from '$lib/stores/modelStore';
	import { apiService } from '$lib/services/apiService';
	import type { ExportFormat } from '$lib/types/model';

	let exporting = false;
	let exportError: string | null = null;

	async function handleExport(format: 'stl' | 'step' | 'iges') {
		if (!$currentModel) return;

		exporting = true;
		exportError = null;

		try {
			const exportFormat: ExportFormat = {
				format,
				options: {
					binary: format === 'stl',
					units: 'm'
				}
			};

			const blob = await apiService.exportModel($currentModel.id, exportFormat);

			// Create download link
			const url = window.URL.createObjectURL(blob);
			const a = document.createElement('a');
			a.href = url;
			a.download = `${$currentModel.name}.${format}`;
			document.body.appendChild(a);
			a.click();
			document.body.removeChild(a);
			window.URL.revokeObjectURL(url);
		} catch (error) {
			exportError = error instanceof Error ? error.message : 'Export failed';
		}

		exporting = false;
	}

	const exportFormats = [
		{ format: 'stl' as const, label: 'STL', description: '3D printing' },
		{ format: 'step' as const, label: 'STEP', description: 'CAD exchange' },
		{ format: 'iges' as const, label: 'IGES', description: 'Legacy CAD' }
	];
</script>

<div class="export-panel">
	{#if !$hasModel}
		<p class="no-model-message">
			Generate a model first to enable export
		</p>
	{:else}
		<div class="export-buttons">
			{#each exportFormats as { format, label, description }}
				<button
					class="export-btn"
					on:click={() => handleExport(format)}
					disabled={exporting}
				>
					<span class="format-label">{label}</span>
					<span class="format-description">{description}</span>
				</button>
			{/each}
		</div>

		{#if exportError}
			<div class="error-message">
				{exportError}
			</div>
		{/if}

		{#if exporting}
			<div class="exporting-message">
				Exporting...
			</div>
		{/if}
	{/if}
</div>

<style>
	.export-panel {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.no-model-message {
		font-size: 0.875rem;
		color: var(--text-secondary);
		text-align: center;
		margin: 0;
		padding: 1rem;
		background: var(--bg-tertiary);
		border-radius: 0.375rem;
	}

	.export-buttons {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.export-btn {
		padding: 0.75rem;
		background: var(--bg-tertiary);
		border: 1px solid var(--border-color);
		border-radius: 0.375rem;
		display: flex;
		flex-direction: column;
		align-items: flex-start;
		gap: 0.25rem;
		transition: all 0.2s;
	}

	.export-btn:hover:not(:disabled) {
		background: var(--bg-primary);
		border-color: var(--accent-primary);
	}

	.export-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.format-label {
		font-weight: 600;
		font-size: 0.875rem;
		color: var(--text-primary);
	}

	.format-description {
		font-size: 0.75rem;
		color: var(--text-secondary);
	}

	.error-message {
		padding: 0.5rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid var(--error);
		border-radius: 0.25rem;
		color: var(--error);
		font-size: 0.75rem;
	}

	.exporting-message {
		padding: 0.5rem;
		background: rgba(59, 130, 246, 0.1);
		border: 1px solid var(--accent-primary);
		border-radius: 0.25rem;
		color: var(--accent-primary);
		font-size: 0.75rem;
		text-align: center;
	}
</style>

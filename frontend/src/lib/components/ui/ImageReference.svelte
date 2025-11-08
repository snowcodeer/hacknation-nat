<script lang="ts">
	import { referenceImage } from '$lib/stores/modelStore';
	import { apiService } from '$lib/services/apiService';

	let fileInput: HTMLInputElement;
	let uploading = false;
	let error: string | null = null;

	async function handleFileChange(event: Event) {
		const target = event.target as HTMLInputElement;
		const file = target.files?.[0];

		if (!file) return;

		// Validate file type
		if (!file.type.startsWith('image/')) {
			error = 'Please select an image file';
			return;
		}

		// Validate file size (max 10MB)
		if (file.size > 10 * 1024 * 1024) {
			error = 'Image must be smaller than 10MB';
			return;
		}

		uploading = true;
		error = null;

		const response = await apiService.uploadReferenceImage(file);

		if (response.success && response.url) {
			$referenceImage = response.url;
		} else {
			error = response.error || 'Failed to upload image';
		}

		uploading = false;
	}

	function clearImage() {
		$referenceImage = null;
		if (fileInput) {
			fileInput.value = '';
		}
	}
</script>

<div class="image-reference">
	{#if !$referenceImage}
		<input
			type="file"
			accept="image/*"
			bind:this={fileInput}
			on:change={handleFileChange}
			disabled={uploading}
			style="display: none;"
		/>

		<button
			class="upload-btn"
			on:click={() => fileInput.click()}
			disabled={uploading}
		>
			{uploading ? 'Uploading...' : 'Upload Reference Image'}
		</button>

		<p class="hint">
			Upload a photo, sketch, or technical drawing for reference
		</p>

		{#if error}
			<div class="error-message">
				{error}
			</div>
		{/if}
	{:else}
		<div class="image-preview">
			<img src={$referenceImage} alt="Reference" />
			<button class="clear-btn" on:click={clearImage}>
				Clear Image
			</button>
		</div>
	{/if}
</div>

<style>
	.image-reference {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.upload-btn {
		padding: 0.75rem 1rem;
		background: var(--bg-tertiary);
		color: var(--text-primary);
		border: 1px dashed var(--border-color);
		border-radius: 0.375rem;
		font-size: 0.875rem;
		transition: all 0.2s;
	}

	.upload-btn:hover:not(:disabled) {
		background: var(--bg-primary);
		border-color: var(--accent-primary);
	}

	.upload-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.hint {
		font-size: 0.75rem;
		color: var(--text-secondary);
		margin: 0;
		text-align: center;
	}

	.error-message {
		padding: 0.5rem;
		background: rgba(239, 68, 68, 0.1);
		border: 1px solid var(--error);
		border-radius: 0.25rem;
		color: var(--error);
		font-size: 0.75rem;
	}

	.image-preview {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	.image-preview img {
		width: 100%;
		height: auto;
		border-radius: 0.375rem;
		border: 1px solid var(--border-color);
	}

	.clear-btn {
		padding: 0.5rem;
		background: var(--bg-tertiary);
		color: var(--text-secondary);
		border: 1px solid var(--border-color);
		border-radius: 0.25rem;
		font-size: 0.75rem;
		transition: all 0.2s;
	}

	.clear-btn:hover {
		background: rgba(239, 68, 68, 0.1);
		border-color: var(--error);
		color: var(--error);
	}
</style>

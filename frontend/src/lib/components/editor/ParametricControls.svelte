<script lang="ts">
	import { parameters, updateParameter, hasModel, isGenerating } from '$lib/stores/modelStore';
	import { apiService } from '$lib/services/apiService';
	import { setModel } from '$lib/stores/modelStore';

	let isUpdating = false;

	async function handleUpdate() {
		isUpdating = true;
		const response = await apiService.updateParameters($parameters);

		if (response.success && response.model) {
			setModel(response.model);
		}

		isUpdating = false;
	}

	$: disabled = $isGenerating || isUpdating || !$hasModel;
</script>

<div class="parametric-controls">
	<!-- Wing Type -->
	<div class="control-group">
		<label for="wingType">Wing Type</label>
		<select
			id="wingType"
			bind:value={$parameters.wingType}
			{disabled}
		>
			<option value="delta">Delta</option>
			<option value="swept">Swept</option>
			<option value="straight">Straight</option>
			<option value="tapered">Tapered</option>
		</select>
	</div>

	<!-- Span -->
	<div class="control-group">
		<label for="span">
			Span: {$parameters.span.toFixed(2)}m
		</label>
		<input
			id="span"
			type="range"
			min="0.5"
			max="5"
			step="0.1"
			value={$parameters.span}
			on:input={(e) => updateParameter('span', parseFloat(e.currentTarget.value))}
			{disabled}
		/>
	</div>

	<!-- Root Chord -->
	<div class="control-group">
		<label for="rootChord">
			Root Chord: {$parameters.rootChord.toFixed(2)}m
		</label>
		<input
			id="rootChord"
			type="range"
			min="0.1"
			max="2"
			step="0.05"
			value={$parameters.rootChord}
			on:input={(e) => updateParameter('rootChord', parseFloat(e.currentTarget.value))}
			{disabled}
		/>
	</div>

	<!-- Tip Chord (for tapered wings) -->
	{#if $parameters.wingType === 'tapered'}
		<div class="control-group">
			<label for="tipChord">
				Tip Chord: {($parameters.tipChord || 0).toFixed(2)}m
			</label>
			<input
				id="tipChord"
				type="range"
				min="0.05"
				max="1"
				step="0.05"
				value={$parameters.tipChord || 0.2}
				on:input={(e) => updateParameter('tipChord', parseFloat(e.currentTarget.value))}
				{disabled}
			/>
		</div>
	{/if}

	<!-- Sweep Angle -->
	<div class="control-group">
		<label for="sweepAngle">
			Sweep: {$parameters.sweepAngle.toFixed(0)}°
		</label>
		<input
			id="sweepAngle"
			type="range"
			min="0"
			max="60"
			step="5"
			value={$parameters.sweepAngle}
			on:input={(e) => updateParameter('sweepAngle', parseFloat(e.currentTarget.value))}
			{disabled}
		/>
	</div>

	<!-- Thickness -->
	<div class="control-group">
		<label for="thickness">
			Thickness: {$parameters.thickness.toFixed(0)}%
		</label>
		<input
			id="thickness"
			type="range"
			min="5"
			max="20"
			step="1"
			value={$parameters.thickness}
			on:input={(e) => updateParameter('thickness', parseFloat(e.currentTarget.value))}
			{disabled}
		/>
	</div>

	<!-- Dihedral -->
	<div class="control-group">
		<label for="dihedral">
			Dihedral: {$parameters.dihedral.toFixed(0)}°
		</label>
		<input
			id="dihedral"
			type="range"
			min="-10"
			max="10"
			step="1"
			value={$parameters.dihedral}
			on:input={(e) => updateParameter('dihedral', parseFloat(e.currentTarget.value))}
			{disabled}
		/>
	</div>

	<!-- Stabilizers -->
	<div class="control-group checkbox-group">
		<label>
			<input
				type="checkbox"
				bind:checked={$parameters.hasVerticalStabilizer}
				{disabled}
			/>
			Vertical Stabilizer
		</label>
	</div>

	<div class="control-group checkbox-group">
		<label>
			<input
				type="checkbox"
				bind:checked={$parameters.hasHorizontalStabilizer}
				{disabled}
			/>
			Horizontal Stabilizer
		</label>
	</div>

	<button
		class="update-btn"
		on:click={handleUpdate}
		disabled={disabled}
	>
		{isUpdating ? 'Updating...' : 'Update Model'}
	</button>
</div>

<style>
	.parametric-controls {
		display: flex;
		flex-direction: column;
		gap: 1rem;
	}

	.control-group {
		display: flex;
		flex-direction: column;
		gap: 0.5rem;
	}

	label {
		font-size: 0.875rem;
		color: var(--text-primary);
		font-weight: 500;
	}

	select,
	input[type='range'] {
		width: 100%;
	}

	select {
		padding: 0.5rem;
		background: var(--bg-tertiary);
		border: 1px solid var(--border-color);
		border-radius: 0.25rem;
		color: var(--text-primary);
		font-size: 0.875rem;
	}

	select:focus {
		outline: none;
		border-color: var(--accent-primary);
	}

	input[type='range'] {
		-webkit-appearance: none;
		appearance: none;
		height: 6px;
		background: var(--bg-tertiary);
		border-radius: 3px;
		outline: none;
	}

	input[type='range']::-webkit-slider-thumb {
		-webkit-appearance: none;
		appearance: none;
		width: 16px;
		height: 16px;
		background: var(--accent-primary);
		border-radius: 50%;
		cursor: pointer;
	}

	input[type='range']::-moz-range-thumb {
		width: 16px;
		height: 16px;
		background: var(--accent-primary);
		border-radius: 50%;
		cursor: pointer;
		border: none;
	}

	input[type='range']:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}

	.checkbox-group {
		flex-direction: row;
		align-items: center;
	}

	.checkbox-group label {
		display: flex;
		align-items: center;
		gap: 0.5rem;
		cursor: pointer;
	}

	.checkbox-group input[type='checkbox'] {
		width: auto;
		cursor: pointer;
	}

	.update-btn {
		padding: 0.75rem 1rem;
		background: var(--accent-primary);
		color: white;
		border: none;
		border-radius: 0.375rem;
		font-weight: 600;
		font-size: 0.875rem;
		transition: background 0.2s;
		margin-top: 0.5rem;
	}

	.update-btn:hover:not(:disabled) {
		background: var(--accent-hover);
	}

	.update-btn:disabled {
		opacity: 0.5;
		cursor: not-allowed;
	}
</style>

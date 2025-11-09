<script lang="ts">
	import Viewer3D from '$lib/components/3d/Viewer3D.svelte';
	import ComponentEditor from '$lib/components/editor/ComponentEditor.svelte';
	import ExportPanel from '$lib/components/ui/ExportPanel.svelte';
	import AircraftChat from '$lib/components/chat/AircraftChat.svelte';
	import {
		aircraft,
		activeComponent,
		completionStatus,
		isAssemblyReady,
		allComponents,
		allComponentsComplete,
		compiledAircraft,
		isCompiling,
		type ComponentType
	} from '$lib/stores/aircraftStore';
	import { apiService } from '$lib/services/apiService';

	type ViewMode = 'edit' | 'assembly';
	let viewMode: ViewMode = 'edit';

	const componentLabels: Record<ComponentType, string> = {
		wings: 'Wings',
		fuselage: 'Fuselage',
		tail_assembly: 'Tail Assembly',
		engines: 'Engines'
	};

	const componentIcons: Record<ComponentType, string> = {
		wings: '✈️',
		fuselage: '🚀',
		tail_assembly: '📐',
		engines: '🔧'
	};

	function selectComponent(type: ComponentType) {
		activeComponent.set(type);
		viewMode = 'edit';
	}

	function goToAssembly() {
		viewMode = 'assembly';
	}

	$: canAssemble = $isAssemblyReady;
	$: assemblyComponentCount = $allComponents.length;
	$: canCompile = $allComponentsComplete && !$compiledAircraft;

	async function handleCompileAircraft() {
		isCompiling.set(true);

		try {
			const response = await apiService.compileAircraft($aircraft);

			if (response.success && response.model) {
				compiledAircraft.set(response.model);
				console.log('Aircraft compiled successfully:', response.model.name);
			} else {
				console.error('Compilation failed:', response.error);
				alert('Failed to compile aircraft: ' + (response.error || 'Unknown error'));
			}
		} catch (error) {
			console.error('Error compiling aircraft:', error);
			alert('Error compiling aircraft');
		} finally {
			isCompiling.set(false);
		}
	}
</script>

<main class="app-container">
	<header class="app-header">
		<div class="header-content">
			<div>
				<h1>AeroCraft</h1>
				<p>AI-Powered Multi-Component Aircraft Designer</p>
			</div>
			<div class="header-stats">
				<div class="component-count">{assemblyComponentCount}/4 Components</div>
				<button
					class="assembly-btn-header"
					class:disabled={!canAssemble}
					disabled={!canAssemble}
					on:click={goToAssembly}
				>
					🔧 Assembly
				</button>
			</div>
		</div>
	</header>

	<div class="workspace">
		<!-- Left: Editor -->
		<section class="editor-area">
			<!-- Chat Interface -->
			<AircraftChat />

			{#if viewMode === 'edit'}
				<div class="editor-header">
					<h2>{componentIcons[$activeComponent]} {componentLabels[$activeComponent]}</h2>
				</div>
				<div class="editor-content">
					<ComponentEditor componentType={$activeComponent} />
				</div>
			{:else}
				<div class="assembly-view">
					<div class="assembly-header">
						<h2>🔧 Assembly View</h2>
						<p>Review your complete aircraft design</p>
					</div>
					<div class="assembly-content">
						<div class="assembly-summary">
							<h3>Components Summary</h3>
							<div class="summary-grid">
								{#each Object.entries(componentLabels) as [type, label]}
									{#if $completionStatus[type]}
										<div class="summary-item complete">
											<span class="summary-icon">{componentIcons[type]}</span>
											<span class="summary-label">{label}</span>
											<span class="summary-check">✓</span>
										</div>
									{:else}
										<div class="summary-item incomplete">
											<span class="summary-icon">{componentIcons[type]}</span>
											<span class="summary-label">{label}</span>
											<span class="summary-status">Not added</span>
										</div>
									{/if}
								{/each}
							</div>
						</div>

						<div class="compile-section">
							<button
								class="compile-btn"
								class:disabled={!canCompile}
								disabled={!canCompile || $isCompiling}
								on:click={handleCompileAircraft}
							>
								{#if $isCompiling}
									⚙️ Compiling...
								{:else if $compiledAircraft}
									✓ Aircraft Compiled
								{:else}
									🔧 Compile Aircraft
								{/if}
							</button>
							{#if !$allComponentsComplete}
								<p class="compile-hint">Complete all 4 components to compile</p>
							{:else if $compiledAircraft}
								<p class="compile-success">Aircraft ready for export!</p>
							{/if}
						</div>

						<div class="export-section">
							<h3>Export Aircraft</h3>
							<ExportPanel />
						</div>
					</div>
				</div>
			{/if}
		</section>

		<!-- Right: 3D Viewer -->
		<section class="viewer-container">
			<div class="viewer-header">
				<h3>3D Preview</h3>
				<span class="viewer-mode">
					{viewMode === 'assembly' ? 'Assembly' : componentLabels[$activeComponent]}
				</span>
			</div>
			<div class="viewer-wrapper">
				<Viewer3D {viewMode} />
			</div>
		</section>
	</div>

	<!-- Component Tabs at Bottom -->
	<nav class="component-tabs">
		{#each Object.entries(componentLabels) as [type, label]}
			<button
				class="tab"
				class:active={$activeComponent === type && viewMode === 'edit'}
				class:completed={$completionStatus[type]}
				on:click={() => selectComponent(type)}
			>
				<span class="tab-icon">{componentIcons[type]}</span>
				<span class="tab-label">{label}</span>
				{#if $completionStatus[type]}
					<span class="tab-status complete">✓</span>
				{:else if $aircraft[type].isGenerating}
					<span class="tab-status generating">...</span>
				{/if}
			</button>
		{/each}
	</nav>
</main>

<style>
	.app-container {
		width: 100vw;
		height: 100vh;
		display: flex;
		flex-direction: column;
		background: #0f172a;
		color: #f1f5f9;
	}

	.app-header {
		padding: 1rem 2rem;
		background: linear-gradient(135deg, #1e293b 0%, #0f172a 100%);
		border-bottom: 2px solid #334155;
	}

	.header-content {
		display: flex;
		justify-content: space-between;
		align-items: center;
	}

	.app-header h1 {
		font-size: 1.75rem;
		margin: 0;
		background: linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%);
		-webkit-background-clip: text;
		-webkit-text-fill-color: transparent;
		background-clip: text;
		font-weight: 700;
	}

	.app-header p {
		margin: 0.25rem 0 0;
		font-size: 0.875rem;
		color: #94a3b8;
	}

	.header-stats {
		display: flex;
		align-items: center;
		gap: 1rem;
	}

	.component-count {
		padding: 0.5rem 1rem;
		background: #1e293b;
		border: 2px solid #334155;
		border-radius: 0.5rem;
		font-size: 0.875rem;
		font-weight: 600;
		color: #60a5fa;
	}

	.assembly-btn-header {
		padding: 0.5rem 1rem;
		background: linear-gradient(135deg, #10b981 0%, #059669 100%);
		border: none;
		border-radius: 0.5rem;
		color: white;
		font-size: 0.875rem;
		font-weight: 600;
		cursor: pointer;
		transition: all 0.2s;
	}

	.assembly-btn-header:not(:disabled):hover {
		transform: translateY(-2px);
		box-shadow: 0 4px 8px rgba(16, 185, 129, 0.3);
	}

	.assembly-btn-header.disabled {
		background: #334155;
		color: #64748b;
		cursor: not-allowed;
		opacity: 0.5;
	}

	.workspace {
		flex: 1;
		display: grid;
		grid-template-columns: minmax(400px, 650px) 1fr;
		overflow: hidden;
	}

	/* Editor Area */
	.editor-area {
		background: #0f172a;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		border-right: 2px solid #334155;
	}

	.editor-header {
		padding: 2rem;
		border-bottom: 2px solid #334155;
	}

	.editor-header h2 {
		font-size: 1.5rem;
		font-weight: 700;
		color: #f1f5f9;
		margin: 0;
	}

	.editor-header p {
		margin: 0.5rem 0 0;
		font-size: 0.875rem;
		color: #94a3b8;
	}

	.editor-content {
		padding: 2rem;
		flex: 1;
	}

	/* Assembly View */
	.assembly-view {
		display: flex;
		flex-direction: column;
		height: 100%;
	}

	.assembly-header {
		padding: 2rem;
		border-bottom: 2px solid #334155;
	}

	.assembly-header h2 {
		font-size: 1.5rem;
		font-weight: 700;
		color: #f1f5f9;
		margin: 0;
	}

	.assembly-header p {
		margin: 0.5rem 0 0;
		font-size: 0.875rem;
		color: #94a3b8;
	}

	.assembly-content {
		padding: 2rem;
		flex: 1;
		overflow-y: auto;
		display: flex;
		flex-direction: column;
		gap: 2rem;
	}

	.assembly-summary h3 {
		font-size: 1rem;
		font-weight: 600;
		color: #f1f5f9;
		margin: 0 0 1rem;
	}

	.summary-grid {
		display: grid;
		gap: 0.75rem;
	}

	.summary-item {
		display: flex;
		align-items: center;
		gap: 0.75rem;
		padding: 1rem;
		background: #1e293b;
		border: 2px solid #334155;
		border-radius: 0.5rem;
	}

	.summary-item.complete {
		border-color: #10b981;
	}

	.summary-icon {
		font-size: 1.25rem;
	}

	.summary-label {
		flex: 1;
		font-size: 0.875rem;
		font-weight: 600;
		color: #f1f5f9;
	}

	.summary-check {
		color: #10b981;
		font-size: 1.25rem;
		font-weight: 700;
	}

	.summary-status {
		font-size: 0.75rem;
		color: #64748b;
	}

	.compile-section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
		padding: 1.5rem;
		background: #1e293b;
		border: 2px solid #334155;
		border-radius: 0.75rem;
	}

	.compile-btn {
		padding: 1rem 1.5rem;
		background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
		border: none;
		border-radius: 0.5rem;
		color: white;
		font-size: 1rem;
		font-weight: 700;
		cursor: pointer;
		transition: all 0.3s;
		box-shadow: 0 4px 12px rgba(139, 92, 246, 0.3);
	}

	.compile-btn:not(:disabled):hover {
		transform: translateY(-2px);
		box-shadow: 0 8px 20px rgba(139, 92, 246, 0.5);
	}

	.compile-btn.disabled {
		background: #334155;
		color: #64748b;
		cursor: not-allowed;
		opacity: 0.6;
		box-shadow: none;
	}

	.compile-hint {
		margin: 0;
		font-size: 0.8125rem;
		color: #94a3b8;
		text-align: center;
	}

	.compile-success {
		margin: 0;
		font-size: 0.8125rem;
		color: #10b981;
		text-align: center;
		font-weight: 600;
	}

	.export-section h3 {
		font-size: 1rem;
		font-weight: 600;
		color: #f1f5f9;
		margin: 0 0 1rem;
	}

	/* 3D Viewer */
	.viewer-container {
		background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
		display: flex;
		flex-direction: column;
		overflow: hidden;
	}

	.viewer-header {
		padding: 1rem 1.5rem;
		background: rgba(30, 41, 59, 0.5);
		border-bottom: 2px solid #334155;
		display: flex;
		justify-content: space-between;
		align-items: center;
		flex-shrink: 0;
	}

	.viewer-header h3 {
		font-size: 0.875rem;
		font-weight: 600;
		color: #94a3b8;
		margin: 0;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.viewer-mode {
		padding: 0.375rem 0.75rem;
		background: #1e293b;
		border: 1px solid #334155;
		border-radius: 0.375rem;
		font-size: 0.75rem;
		font-weight: 600;
		color: #60a5fa;
	}

	.viewer-wrapper {
		flex: 1;
		position: relative;
		min-height: 0;
		overflow: hidden;
	}

	/* Component Tabs */
	.component-tabs {
		display: flex;
		background: #1e293b;
		border-top: 2px solid #334155;
		padding: 0;
		flex-shrink: 0;
	}

	.tab {
		flex: 1;
		display: flex;
		flex-direction: column;
		align-items: center;
		justify-content: center;
		gap: 0.5rem;
		padding: 1rem;
		background: transparent;
		border: none;
		border-right: 1px solid #334155;
		color: #94a3b8;
		cursor: pointer;
		transition: all 0.2s;
		position: relative;
	}

	.tab:last-child {
		border-right: none;
	}

	.tab:hover {
		background: #0f172a;
		color: #f1f5f9;
	}

	.tab.active {
		background: #0f172a;
		color: #3b82f6;
		border-top: 3px solid #3b82f6;
	}

	.tab.completed {
		color: #10b981;
	}

	.tab.completed.active {
		color: #3b82f6;
	}

	.tab-icon {
		font-size: 1.5rem;
	}

	.tab-label {
		font-size: 0.75rem;
		font-weight: 600;
		text-transform: uppercase;
		letter-spacing: 0.05em;
	}

	.tab-status {
		position: absolute;
		top: 0.5rem;
		right: 0.5rem;
		font-size: 0.875rem;
	}

	.tab-status.complete {
		color: #10b981;
	}

	.tab-status.generating {
		color: #3b82f6;
		animation: pulse 1.5s infinite;
	}

	@keyframes pulse {
		0%, 100% {
			opacity: 1;
		}
		50% {
			opacity: 0.5;
		}
	}
</style>

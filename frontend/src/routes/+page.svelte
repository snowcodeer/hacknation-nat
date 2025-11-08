<script lang="ts">
	import Viewer3D from '$lib/components/3d/Viewer3D.svelte';
	import ParametricControls from '$lib/components/editor/ParametricControls.svelte';
	import TextPrompt from '$lib/components/ui/TextPrompt.svelte';
	import ImageReference from '$lib/components/ui/ImageReference.svelte';
	import ExportPanel from '$lib/components/ui/ExportPanel.svelte';
</script>

<main class="app-container">
	<header class="app-header">
		<h1>AeroCraft</h1>
		<p>AI-Powered Aerospace CAD</p>
	</header>

	<div class="workspace">
		<!-- Left panel: Input and controls -->
		<aside class="left-panel">
			<div class="panel-section">
				<h2>Generate</h2>
				<TextPrompt />
			</div>

			<div class="panel-section">
				<h2>Parameters</h2>
				<ParametricControls />
			</div>

			<div class="panel-section">
				<h2>Reference</h2>
				<ImageReference />
			</div>

			<div class="panel-section">
				<h2>Export</h2>
				<ExportPanel />
			</div>
		</aside>

		<!-- Center: 3D Viewer -->
		<section class="viewer-container">
			<Viewer3D />
		</section>
	</div>
</main>

<style>
	.app-container {
		width: 100vw;
		height: 100vh;
		display: flex;
		flex-direction: column;
		background: var(--bg-primary);
	}

	.app-header {
		padding: 1rem 2rem;
		background: var(--bg-secondary);
		border-bottom: 1px solid var(--border-color);
	}

	.app-header h1 {
		font-size: 1.5rem;
		margin: 0;
		color: var(--accent-primary);
	}

	.app-header p {
		margin: 0.25rem 0 0;
		font-size: 0.875rem;
		color: var(--text-secondary);
	}

	.workspace {
		flex: 1;
		display: flex;
		overflow: hidden;
	}

	.left-panel {
		width: 320px;
		background: var(--bg-secondary);
		border-right: 1px solid var(--border-color);
		overflow-y: auto;
		padding: 1rem;
		display: flex;
		flex-direction: column;
		gap: 1.5rem;
	}

	.panel-section {
		display: flex;
		flex-direction: column;
		gap: 0.75rem;
	}

	.panel-section h2 {
		font-size: 1rem;
		color: var(--text-primary);
		margin: 0;
		padding-bottom: 0.5rem;
		border-bottom: 1px solid var(--border-color);
	}

	.viewer-container {
		flex: 1;
		position: relative;
		background: linear-gradient(135deg, #1e3a8a 0%, #0f172a 100%);
	}
</style>

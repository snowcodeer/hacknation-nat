<script lang="ts">
	import { Canvas } from '@threlte/core';
	import Scene from './Scene.svelte';
</script>

<div class="viewer-3d">
	<Canvas>
		<Scene />
	</Canvas>
</div>

<style>
	.viewer-3d {
		width: 100%;
		height: 100%;
		position: relative;
	}
</style>

<script lang="ts">
	import { T } from '@threlte/core';
	import { OrbitControls, Grid } from '@threlte/extras';
	import AeroModel from './AeroModel.svelte';
	import { currentModel } from '$lib/stores/modelStore';
</script>

<!-- Camera -->
<T.PerspectiveCamera
	makeDefault
	position={[5, 3, 5]}
	fov={50}
>
	<OrbitControls
		enableDamping
		dampingFactor={0.05}
		autoRotate={false}
		autoRotateSpeed={0.5}
		target={{ x: 0, y: 0, z: 0 }}
	/>
</T.PerspectiveCamera>

<!-- Lighting -->
<T.AmbientLight intensity={0.4} />
<T.DirectionalLight
	position={[10, 10, 5]}
	intensity={1}
	castShadow
/>
<T.DirectionalLight
	position={[-10, 10, -5]}
	intensity={0.5}
/>

<!-- Grid -->
<Grid
	infiniteGrid
	sectionColor="#3b82f6"
	sectionSize={1}
	cellColor="#475569"
	cellSize={0.5}
	fadeDistance={30}
	fadeStrength={1}
/>

<!-- 3D Model -->
{#if $currentModel}
	<AeroModel model={$currentModel} />
{:else}
	<!-- Placeholder: Show a simple wing when no model -->
	<T.Group position={[0, 0.5, 0]}>
		<T.Mesh>
			<T.BoxGeometry args={[2, 0.1, 0.5]} />
			<T.MeshStandardMaterial
				color="#3b82f6"
				metalness={0.3}
				roughness={0.4}
			/>
		</T.Mesh>
	</T.Group>
{/if}

<!-- Axes Helper (for debugging) -->
<T.AxesHelper args={[2]} />

<script lang="ts">
	import { T } from '@threlte/core';
	import { OrbitControls } from '@threlte/extras';
	import AeroModel from './AeroModel.svelte';
	import { currentModel } from '$lib/stores/modelStore';
</script>

<!-- Camera -->
<T.PerspectiveCamera
	makeDefault
	position={[3, 2, 3]}
	fov={75}
>
	<OrbitControls enableDamping target={{ x: 0, y: 0, z: 0 }} />
</T.PerspectiveCamera>

<!-- Lighting -->
<T.AmbientLight intensity={0.6} />
<T.DirectionalLight position={[5, 5, 5]} intensity={1.2} castShadow />
<T.DirectionalLight position={[-5, 3, -5]} intensity={0.5} />

<!-- Ground plane for reference -->
<T.Mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.01, 0]} receiveShadow>
	<T.PlaneGeometry args={[10, 10]} />
	<T.MeshStandardMaterial color="#1e293b" />
</T.Mesh>

<!-- Model -->
{#if $currentModel}
	<AeroModel model={$currentModel} />
{/if}

<!-- Axes helper for orientation -->
<T.AxesHelper args={[2]} />

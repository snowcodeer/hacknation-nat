<script lang="ts">
	import { T } from '@threlte/core';
	import type { Model3D } from '$lib/types/model';
	import { BufferGeometry, BufferAttribute, DoubleSide } from 'three';
	import { onMount } from 'svelte';

	export let model: Model3D;

	let geometry: BufferGeometry | undefined;

	$: if (model) {
		updateGeometry();
	}

	function updateGeometry() {
		geometry = new BufferGeometry();

		if (model.geometry.vertices && model.geometry.indices) {
			geometry.setAttribute(
				'position',
				new BufferAttribute(model.geometry.vertices, 3)
			);

			geometry.setIndex(new BufferAttribute(model.geometry.indices, 1));

			if (model.geometry.normals) {
				geometry.setAttribute(
					'normal',
					new BufferAttribute(model.geometry.normals, 3)
				);
			} else {
				geometry.computeVertexNormals();
			}
		}
	}

	onMount(() => {
		updateGeometry();
	});
</script>

{#if geometry}
	<T.Group position={[0, 0.5, 0]}>
		<T.Mesh
			geometry={geometry}
			receiveShadow
			castShadow
		>
			<T.MeshStandardMaterial
				color="#3b82f6"
				metalness={0.4}
				roughness={0.3}
				side={DoubleSide}
			/>
		</T.Mesh>

		<!-- Wireframe overlay -->
		<T.Mesh
			geometry={geometry}
		>
			<T.MeshBasicMaterial
				color="#60a5fa"
				wireframe
				transparent
				opacity={0.3}
			/>
		</T.Mesh>
	</T.Group>
{/if}

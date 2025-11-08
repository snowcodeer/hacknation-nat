<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
	import { aircraft, activeComponent, allComponents } from '$lib/stores/aircraftStore';

	export let viewMode: 'edit' | 'assembly' = 'edit';

	let container: HTMLDivElement;
	let renderer: THREE.WebGLRenderer;
	let scene: THREE.Scene;
	let camera: THREE.PerspectiveCamera;
	let controls: OrbitControls;
	let modelMeshes: THREE.Group = new THREE.Group();
	let animationId: number;

	const componentColors: Record<string, number> = {
		wings: 0x3b82f6,          // Blue
		fuselage: 0x10b981,       // Green
		tail_assembly: 0xf59e0b,  // Orange
		engines: 0x8b5cf6         // Purple
	};

	function init() {
		// Scene
		scene = new THREE.Scene();
		scene.background = new THREE.Color(0x1e3a8a);

		// Get container dimensions
		const width = container.clientWidth || 800;
		const height = container.clientHeight || 600;

		// Camera
		camera = new THREE.PerspectiveCamera(
			75,
			width / height,
			0.1,
			1000
		);
		camera.position.set(3, 2, 3);
		camera.lookAt(0, 0, 0);

		// Renderer
		renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setSize(width, height);
		renderer.setPixelRatio(window.devicePixelRatio);
		renderer.shadowMap.enabled = true;
		container.appendChild(renderer.domElement);

		// Controls
		controls = new OrbitControls(camera, renderer.domElement);
		controls.enableDamping = true;
		controls.dampingFactor = 0.05;
		controls.target.set(0, 0, 0);

		// Lights
		const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
		scene.add(ambientLight);

		const directionalLight1 = new THREE.DirectionalLight(0xffffff, 1.2);
		directionalLight1.position.set(5, 5, 5);
		directionalLight1.castShadow = true;
		scene.add(directionalLight1);

		const directionalLight2 = new THREE.DirectionalLight(0xffffff, 0.5);
		directionalLight2.position.set(-5, 3, -5);
		scene.add(directionalLight2);

		// Ground plane
		const groundGeometry = new THREE.PlaneGeometry(10, 10);
		const groundMaterial = new THREE.MeshStandardMaterial({ color: 0x1e293b });
		const ground = new THREE.Mesh(groundGeometry, groundMaterial);
		ground.rotation.x = -Math.PI / 2;
		ground.position.y = -0.01;
		ground.receiveShadow = true;
		scene.add(ground);

		// Axes helper
		const axesHelper = new THREE.AxesHelper(2);
		scene.add(axesHelper);

		// Add model group to scene
		scene.add(modelMeshes);

		// Handle window resize
		window.addEventListener('resize', onWindowResize);

		// Start animation loop
		animate();
	}

	function onWindowResize() {
		if (!container || !camera || !renderer) return;

		camera.aspect = container.clientWidth / container.clientHeight;
		camera.updateProjectionMatrix();
		renderer.setSize(container.clientWidth, container.clientHeight);
	}

	function animate() {
		animationId = requestAnimationFrame(animate);

		if (controls) controls.update();
		if (renderer && scene && camera) {
			renderer.render(scene, camera);
		}
	}

	function createMeshFromModel(model: any, componentType: string, position: THREE.Vector3) {
		// Create geometry
		const geometry = new THREE.BufferGeometry();

		const vertices = new Float32Array(model.geometry.vertices);
		const indices = new Uint32Array(model.geometry.indices);

		geometry.setAttribute('position', new THREE.BufferAttribute(vertices, 3));
		geometry.setIndex(new THREE.BufferAttribute(indices, 1));

		if (model.geometry.normals) {
			const normals = new Float32Array(model.geometry.normals);
			geometry.setAttribute('normal', new THREE.BufferAttribute(normals, 3));
		} else {
			geometry.computeVertexNormals();
		}

		// Create material with component-specific color
		const color = componentColors[componentType] || 0x3b82f6;
		const material = new THREE.MeshStandardMaterial({
			color,
			metalness: 0.4,
			roughness: 0.3,
			side: THREE.DoubleSide
		});

		// Create mesh
		const mesh = new THREE.Mesh(geometry, material);
		mesh.position.copy(position);
		mesh.castShadow = true;
		mesh.receiveShadow = true;

		return { mesh, geometry };
	}

	function updateModels() {
		if (!scene) return;

		// Clear existing models
		modelMeshes.clear();

		if (viewMode === 'assembly') {
			// Show all components in assembly mode
			const aircraftData = $aircraft;

			// Wings - centered
			if (aircraftData.wings.model) {
				const { mesh, geometry } = createMeshFromModel(
					aircraftData.wings.model,
					'wings',
					new THREE.Vector3(0, 0.5, 0)
				);
				modelMeshes.add(mesh);

				// Add wireframe
				const wireframeMaterial = new THREE.MeshBasicMaterial({
					color: componentColors.wings,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const wireframe = new THREE.Mesh(geometry.clone(), wireframeMaterial);
				wireframe.position.copy(mesh.position);
				modelMeshes.add(wireframe);
			}

			// Fuselage - centered
			if (aircraftData.fuselage.model) {
				const { mesh, geometry } = createMeshFromModel(
					aircraftData.fuselage.model,
					'fuselage',
					new THREE.Vector3(0, 0.5, 0)
				);
				modelMeshes.add(mesh);

				// Add wireframe
				const wireframeMaterial = new THREE.MeshBasicMaterial({
					color: componentColors.fuselage,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const wireframe = new THREE.Mesh(geometry.clone(), wireframeMaterial);
				wireframe.position.copy(mesh.position);
				modelMeshes.add(wireframe);
			}

			// Tail assembly - behind at tail position
			if (aircraftData.tail_assembly.model) {
				const { mesh, geometry } = createMeshFromModel(
					aircraftData.tail_assembly.model,
					'tail_assembly',
					new THREE.Vector3(0, 0.6, -1.2)
				);
				modelMeshes.add(mesh);

				// Add wireframe
				const wireframeMaterial = new THREE.MeshBasicMaterial({
					color: componentColors.tail_assembly,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const wireframe = new THREE.Mesh(geometry.clone(), wireframeMaterial);
				wireframe.position.copy(mesh.position);
				modelMeshes.add(wireframe);
			}

			// Engines - under wings
			if (aircraftData.engines.model) {
				const { mesh, geometry } = createMeshFromModel(
					aircraftData.engines.model,
					'engines',
					new THREE.Vector3(0, 0.2, 0.3)
				);
				modelMeshes.add(mesh);

				// Add wireframe
				const wireframeMaterial = new THREE.MeshBasicMaterial({
					color: componentColors.engines,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const wireframe = new THREE.Mesh(geometry.clone(), wireframeMaterial);
				wireframe.position.copy(mesh.position);
				modelMeshes.add(wireframe);
			}

			console.log('Assembly view: Showing', $allComponents.length, 'components');
		} else {
			// Show only active component in edit mode
			const activeComp = $aircraft[$activeComponent];
			if (!activeComp || !activeComp.model) return;

			const model = activeComp.model;
			const { mesh, geometry } = createMeshFromModel(
				model,
				$activeComponent,
				new THREE.Vector3(0, 0.5, 0)
			);
			modelMeshes.add(mesh);

			// Add wireframe
			const color = componentColors[$activeComponent] || 0x3b82f6;
			const wireframeMaterial = new THREE.MeshBasicMaterial({
				color,
				wireframe: true,
				transparent: true,
				opacity: 0.3
			});
			const wireframe = new THREE.Mesh(geometry.clone(), wireframeMaterial);
			wireframe.position.copy(mesh.position);
			modelMeshes.add(wireframe);

			console.log('Edit mode: Showing', model.name);
		}
	}

	onMount(() => {
		init();

		return () => {
			// Cleanup
			if (animationId) cancelAnimationFrame(animationId);
			if (controls) controls.dispose();
			if (renderer) {
				renderer.dispose();
				if (container && renderer.domElement) {
					container.removeChild(renderer.domElement);
				}
			}
			window.removeEventListener('resize', onWindowResize);
		};
	});

	// React to model changes
	$: if (scene && $aircraft && ($activeComponent || viewMode === 'assembly')) {
		updateModels();
	}

	// React to view mode changes
	$: if (scene && viewMode) {
		updateModels();
	}
</script>

<div class="viewer-3d" bind:this={container}></div>

<style>
	.viewer-3d {
		width: 100%;
		height: 100%;
		position: relative;
	}
</style>

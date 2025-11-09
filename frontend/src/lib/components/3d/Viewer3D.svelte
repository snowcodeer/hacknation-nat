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
		ground.position.y = -2.0;  // Move ground down to prevent clipping
		ground.receiveShadow = true;
		scene.add(ground);

		// Axes helper - positioned on the ground plane
		const axesHelper = new THREE.AxesHelper(2);
		axesHelper.position.y = -2.0;  // Match ground plane position
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
			// Show all components in assembly mode with proper positioning
			const aircraftData = $aircraft;

			// Calculate fuselage radius for wing positioning
			let fuselageRadius = 0.7; // Default fallback
			if (aircraftData.fuselage.model?.parameters?.fuselageDiameter) {
				fuselageRadius = aircraftData.fuselage.model.parameters.fuselageDiameter / 2;
			}

			// Fuselage - centered (origin) - this is the reference point
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

			// Wings - duplicate for left and right, extending from fuselage sides
			if (aircraftData.wings.model) {
				// Position wings at the fuselage surface (flat mounting edge, no gap)
				const wingOffset = fuselageRadius;

				// Right wing (positive Z) - extending to the right
				const { mesh: rightWing, geometry: rightGeom } = createMeshFromModel(
					aircraftData.wings.model,
					'wings',
					new THREE.Vector3(0, 0.5, 0)  // Centered at fuselage
				);
				// Wings now generated in correct orientation - no rotation needed
				rightWing.position.z = wingOffset;  // Outside fuselage surface
				modelMeshes.add(rightWing);

				const rightWireframe = new THREE.MeshBasicMaterial({
					color: componentColors.wings,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const rightWireframeMesh = new THREE.Mesh(rightGeom.clone(), rightWireframe);
				rightWireframeMesh.position.copy(rightWing.position);
				modelMeshes.add(rightWireframeMesh);

				// Left wing (negative Z) - extending to the left
				const { mesh: leftWing, geometry: leftGeom } = createMeshFromModel(
					aircraftData.wings.model,
					'wings',
					new THREE.Vector3(0, 0.5, 0)  // Centered at fuselage
				);
				// Wings now generated in correct orientation - just mirror for left side
				leftWing.scale.z = -1;  // Mirror across Z for left wing
				leftWing.position.z = -wingOffset;  // Outside fuselage surface
				modelMeshes.add(leftWing);

				const leftWireframe = new THREE.MeshBasicMaterial({
					color: componentColors.wings,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const leftWireframeMesh = new THREE.Mesh(leftGeom.clone(), leftWireframe);
				leftWireframeMesh.scale.z = -1;  // Mirror across Z for left wing
				leftWireframeMesh.position.copy(leftWing.position);
				modelMeshes.add(leftWireframeMesh);
			}


			// Engines - duplicate for left and right, positioned under wings on either side
			if (aircraftData.engines.model) {
				// Calculate wing span to position engines properly
				const wingSpan = aircraftData.wings.model?.parameters?.span || 10;
				const engineOffsetZ = (wingSpan / 2) * 0.6;  // Place engines 60% out along wing span

				// Right engine (positive Z) - under right wing, attached
				const { mesh: rightEngine, geometry: rightEngGeom } = createMeshFromModel(
					aircraftData.engines.model,
					'engines',
					new THREE.Vector3(0, 0, engineOffsetZ)  // Aligned with wing, hanging below
				);
				modelMeshes.add(rightEngine);

				const rightEngWireframe = new THREE.MeshBasicMaterial({
					color: componentColors.engines,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const rightEngWireframeMesh = new THREE.Mesh(rightEngGeom.clone(), rightEngWireframe);
				rightEngWireframeMesh.position.copy(rightEngine.position);
				modelMeshes.add(rightEngWireframeMesh);

				// Left engine (negative Z) - under left wing, attached
				const { mesh: leftEngine, geometry: leftEngGeom } = createMeshFromModel(
					aircraftData.engines.model,
					'engines',
					new THREE.Vector3(0, 0, -engineOffsetZ)  // Aligned with wing, hanging below
				);
				modelMeshes.add(leftEngine);

				const leftEngWireframe = new THREE.MeshBasicMaterial({
					color: componentColors.engines,
					wireframe: true,
					transparent: true,
					opacity: 0.2
				});
				const leftEngWireframeMesh = new THREE.Mesh(leftEngGeom.clone(), leftEngWireframe);
				leftEngWireframeMesh.position.copy(leftEngine.position);
				modelMeshes.add(leftEngWireframeMesh);
			}

			console.log('Assembly view: Showing', $allComponents.length, 'components with proper positioning');
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

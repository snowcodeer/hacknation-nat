<script lang="ts">
	import { onMount } from 'svelte';
	import * as THREE from 'three';
	import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';
	import { currentModel } from '$lib/stores/modelStore';

	let container: HTMLDivElement;
	let renderer: THREE.WebGLRenderer;
	let scene: THREE.Scene;
	let camera: THREE.PerspectiveCamera;
	let controls: OrbitControls;
	let modelMesh: THREE.Mesh | null = null;
	let animationId: number;

	function init() {
		// Scene
		scene = new THREE.Scene();
		scene.background = new THREE.Color(0x1e3a8a);

		// Camera
		camera = new THREE.PerspectiveCamera(
			75,
			container.clientWidth / container.clientHeight,
			0.1,
			1000
		);
		camera.position.set(3, 2, 3);
		camera.lookAt(0, 0, 0);

		// Renderer
		renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setSize(container.clientWidth, container.clientHeight);
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

	function updateModel(model: typeof $currentModel) {
		if (!scene || !model) return;

		// Remove old mesh
		if (modelMesh) {
			scene.remove(modelMesh);
			modelMesh.geometry.dispose();
			if (Array.isArray(modelMesh.material)) {
				modelMesh.material.forEach(m => m.dispose());
			} else {
				modelMesh.material.dispose();
			}
		}

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

		// Create material
		const material = new THREE.MeshStandardMaterial({
			color: 0x3b82f6,
			metalness: 0.4,
			roughness: 0.3,
			side: THREE.DoubleSide
		});

		// Create mesh
		modelMesh = new THREE.Mesh(geometry, material);
		modelMesh.position.set(0, 0.5, 0);
		modelMesh.castShadow = true;
		modelMesh.receiveShadow = true;
		scene.add(modelMesh);

		// Add wireframe
		const wireframeGeometry = geometry.clone();
		const wireframeMaterial = new THREE.MeshBasicMaterial({
			color: 0x60a5fa,
			wireframe: true,
			transparent: true,
			opacity: 0.3
		});
		const wireframe = new THREE.Mesh(wireframeGeometry, wireframeMaterial);
		wireframe.position.copy(modelMesh.position);
		scene.add(wireframe);

		console.log('Model added to scene:', model.name);
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
	$: if (scene && $currentModel) {
		updateModel($currentModel);
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

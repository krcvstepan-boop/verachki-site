const vertexShader = `
precision mediump float;
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vViewPosition;
uniform float uTime;

void main() {
    vUv = uv;
    vNormal = normalize(normalMatrix * normal);

    // Breathing: sine wave displacement along normal
    vec3 newPos = position + normal * sin(uTime * 2.0) * 0.05;

    vec4 mvPosition = modelViewMatrix * vec4(newPos, 1.0);
    vViewPosition = -mvPosition.xyz;
    gl_Position = projectionMatrix * mvPosition;
}
`;

const fragmentShader = `
precision mediump float;
varying vec2 vUv;
varying vec3 vNormal;
varying vec3 vViewPosition;
uniform float uTime;
uniform vec3 uColor;

void main() {
    vec3 normal = normalize(vNormal);
    vec3 viewDir = normalize(vViewPosition);

    // Fresnel
    float fresnel = pow(1.0 - abs(dot(viewDir, normal)), 3.0);

    // Dynamic Pastel Gradient
    vec3 pink = vec3(1.0, 0.82, 0.86);
    vec3 cyan = vec3(0.68, 0.85, 0.9);
    float t = uTime * 0.5;
    float mixVal = sin(vUv.y * 3.0 + t) * 0.5 + 0.5;
    vec3 gradient = mix(pink, cyan, mixVal);

    // Fake Chromatic Dispersion (prism)
    vec3 disp = vec3(0.0);
    disp.r = sin(dot(viewDir, normal) * 10.0 + t) * 0.5 + 0.5;
    disp.g = sin(dot(viewDir, normal) * 10.0 + t + 2.0) * 0.5 + 0.5;
    disp.b = sin(dot(viewDir, normal) * 10.0 + t + 4.0) * 0.5 + 0.5;

    vec3 finalColor = mix(gradient, uColor, 0.3);
    finalColor += disp * 0.2 * fresnel;
    finalColor += fresnel * 0.8; // Edge glow

    float alpha = 0.5 + fresnel * 0.5;

    gl_FragColor = vec4(finalColor, alpha);
}
`;


class SoulAvatarSystem {
    constructor() {
        this.canvas = document.getElementById('soul-avatars');
        this.renderer = null;
        this.container = document.getElementById('messages-container');
        this.isRunning = false;

        // Caches
        this.meshes = new Map(); // username -> { group, speed, rotationAxis }

        // Single Shared Resources
        this.scene = null;
        this.camera = null;
        // Shared material removed as per new multi-color requirement

        // Configuration
        this.baseColor = 0x6a4df4;
        this.secondaryColor = 0x74b9ff;

        // Profile Renderer State
        this.profileRenderer = null;
        this.profileScene = null;
        this.profileCamera = null;
        this.profileGroup = null;
        this.profileCanvas = null;
        this.profileRequestId = null;

        // Optimization: Intersection Observer
        this.visibleAvatars = new Set();
        this.observer = null;
        this.mutationObserver = null;
    }

    init() {
        if (!this.canvas || !window.THREE) return;

        // Optimization: High Performance Mode
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            alpha: true,
            antialias: true,
            powerPreference: "high-performance",
            precision: "mediump"
        });

        this.renderer.setClearColor(0xffffff, 0);

        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Setup Shared Scene
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
        this.camera.position.z = 3.5;

        // Shared Lighting
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.6);
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0xffffff, 0.8);
        pointLight.position.set(5, 5, 5);
        this.scene.add(pointLight);

        const pointLight2 = new THREE.PointLight(this.secondaryColor, 0.8);
        pointLight2.position.set(-5, -5, 2);
        this.scene.add(pointLight2);

        // Additional Color Lights for Glass Effect
        const cyanLight = new THREE.PointLight(0x00ffff, 1, 10);
        cyanLight.position.set(2, 2, 2);
        this.scene.add(cyanLight);

        const magentaLight = new THREE.PointLight(0xff00ff, 1, 10);
        magentaLight.position.set(-2, -2, 2);
        this.scene.add(magentaLight);

        // Start animation loop
        this.isRunning = true;
        this.setupObservers();
        this.animate();
        console.log("Soul ID System Initialized (Living Flower Mode)");
    }

    resize() {
        if (!this.renderer) return;
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        if (this.canvas.width !== width || this.canvas.height !== height) {
            this.renderer.setSize(width, height, false);
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        }
    }

    setupObservers() {
        // Observer for visibility
        this.observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    this.visibleAvatars.add(entry.target);
                } else {
                    this.visibleAvatars.delete(entry.target);
                }
            });
        }, {
            root: null,
            rootMargin: '200px', // Preload before it enters viewport
            threshold: 0
        });

        // Observer for new messages
        this.mutationObserver = new MutationObserver((mutations) => {
            mutations.forEach(mutation => {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === 1) { // ELEMENT_NODE
                        // Check if node itself is placeholder
                        if (node.classList.contains('soul-avatar-placeholder')) {
                            this.observer.observe(node);
                        } else {
                            // Check children
                            const placeholders = node.querySelectorAll('.soul-avatar-placeholder');
                            placeholders.forEach(el => this.observer.observe(el));
                        }
                    }
                });

                mutation.removedNodes.forEach(node => {
                    if (node.nodeType === 1) {
                        if (node.classList.contains('soul-avatar-placeholder')) {
                            this.visibleAvatars.delete(node);
                            this.observer.unobserve(node);
                        } else {
                            const placeholders = node.querySelectorAll('.soul-avatar-placeholder');
                            placeholders.forEach(el => {
                                this.visibleAvatars.delete(el);
                                this.observer.unobserve(el);
                            });
                        }
                    }
                });
            });
        });

        if (this.container) {
            this.mutationObserver.observe(this.container, { childList: true, subtree: true });
        }

        // Initial scan
        document.querySelectorAll('.soul-avatar-placeholder').forEach(el => {
            this.observer.observe(el);
        });
    }

    stringToHash(str) {
        let hash = 0;
        for (let i = 0; i < str.length; i++) {
            const char = str.charCodeAt(i);
            hash = ((hash << 5) - hash) + char;
            hash = hash & hash;
        }
        return Math.abs(hash);
    }

    createAvatarGroup(username, xp) {
        const hash = this.stringToHash(username);
        const group = new THREE.Group();

        let seed = hash;
        const random = () => {
            const x = Math.sin(seed++) * 10000;
            return x - Math.floor(x);
        };

        // Pastel Colors: Rose, Blue, Green, Lavender, Peach
        const colors = [0xffd1dc, 0xadd8e6, 0x98fb98, 0xe6e6fa, 0xffdab9];

        // 1. Generate Petals
        const petalCount = 5 + Math.floor(random() * 2); // 5-7 petals
        const amplitude = 0.1 + (Math.min(xp, 100) * 0.002);

        for (let k = 0; k < petalCount; k++) {
            const geometry = new THREE.SphereGeometry(1, 64, 64);
            const positionAttribute = geometry.attributes.position;
            const vertex = new THREE.Vector3();

            // Unique seed offset per petal
            let petalSeed = seed + k * 100;

            for (let i = 0; i < positionAttribute.count; i++) {
                vertex.fromBufferAttribute(positionAttribute, i);
                const angle = Math.atan2(vertex.z, vertex.x);
                const elevation = vertex.y;

                // Soft overlapping curves displacement
                const displacement = 1.0 + amplitude *
                                       Math.sin(5 * angle + petalSeed) *
                                       Math.cos(3 * elevation);

                vertex.multiplyScalar(displacement);
                positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z);
            }

            geometry.computeVertexNormals();

            // Unique Material per Petal
            const colorHex = colors[Math.floor(random() * colors.length)];
            const material = new THREE.ShaderMaterial({
                uniforms: {
                    uTime: { value: 0.0 },
                    uColor: { value: new THREE.Color(colorHex) }
                },
                vertexShader: vertexShader,
                fragmentShader: fragmentShader,
                transparent: true,
                side: THREE.FrontSide
            });

            const mesh = new THREE.Mesh(geometry, material);

            // Random slight rotation to layer them
            mesh.rotation.set(random() * Math.PI, random() * Math.PI, random() * Math.PI);
            mesh.scale.setScalar(0.95 + random() * 0.1);

            group.add(mesh);
        }

        // 2. Add Particles (Magic Atmosphere)
        const particleCount = 60;
        const particleGeo = new THREE.BufferGeometry();
        const positions = new Float32Array(particleCount * 3);

        for(let i=0; i<particleCount; i++) {
            const r = 1.2 + random() * 1.5; // Orbit radius
            const theta = random() * Math.PI * 2;
            const phi = Math.acos(2 * random() - 1);

            positions[i*3] = r * Math.sin(phi) * Math.cos(theta);
            positions[i*3+1] = r * Math.sin(phi) * Math.sin(theta);
            positions[i*3+2] = r * Math.cos(phi);
        }
        particleGeo.setAttribute('position', new THREE.BufferAttribute(positions, 3));

        const particleMat = new THREE.PointsMaterial({
            color: 0x00ffff,
            size: 0.03,
            transparent: true,
            opacity: 0.6,
            blending: THREE.AdditiveBlending
        });

        const particles = new THREE.Points(particleGeo, particleMat);
        group.add(particles);

        const baseSpeed = 0.005 + (xp * 0.0001);

        return {
            group: group,
            speed: baseSpeed + (random() * 0.01),
            rotationAxis: new THREE.Vector3(random()-0.5, random()-0.5, random()-0.5).normalize()
        };
    }

    getMesh(username, xp = 0) {
        if (this.meshes.has(username)) {
            return this.meshes.get(username);
        }

        const data = this.createAvatarGroup(username, xp);
        this.meshes.set(username, data);
        return data;
    }

    updateAvatar(username, xp) {
        if (this.meshes.has(username)) {
            const oldData = this.meshes.get(username);
            // Dispose old resources
            oldData.group.traverse((child) => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) child.material.forEach(m => m.dispose());
                    else child.material.dispose();
                }
            });
            this.meshes.delete(username);
        }
        // Force regeneration
        this.getMesh(username, xp);
    }

    renderProfileAvatar(canvas, username, xp) {
        if (!window.THREE) return;

        if (this.profileRequestId) {
            cancelAnimationFrame(this.profileRequestId);
            this.profileRequestId = null;
        }

        if (!this.profileRenderer || this.profileCanvas !== canvas) {
            if (this.profileRenderer) this.profileRenderer.dispose();

            this.profileCanvas = canvas;
            this.profileRenderer = new THREE.WebGLRenderer({
                canvas: canvas,
                alpha: true,
                antialias: true,
                powerPreference: "high-performance"
            });
            this.profileRenderer.setClearColor(0xffffff, 0);
            this.profileRenderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            this.profileScene = new THREE.Scene();
            this.profileCamera = new THREE.PerspectiveCamera(50, canvas.width / canvas.height, 0.1, 100);
            this.profileCamera.position.z = 3.5;

            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            this.profileScene.add(ambientLight);
            const pointLight = new THREE.PointLight(0xffffff, 1);
            pointLight.position.set(5, 5, 5);
            this.profileScene.add(pointLight);
            const pointLight2 = new THREE.PointLight(this.secondaryColor, 0.8);
            pointLight2.position.set(-5, -5, 2);
            this.profileScene.add(pointLight2);
        }

        const width = canvas.clientWidth;
        const height = canvas.clientHeight;
        if (canvas.width !== width || canvas.height !== height) {
             this.profileRenderer.setSize(width, height, false);
             this.profileCamera.aspect = width / height;
             this.profileCamera.updateProjectionMatrix();
        }

        // Cleanup old profile mesh
        if (this.profileGroup) {
            this.profileScene.remove(this.profileGroup);
            this.profileGroup.traverse((child) => {
                if (child.geometry) child.geometry.dispose();
                if (child.material) {
                    if (Array.isArray(child.material)) child.material.forEach(m => m.dispose());
                    else child.material.dispose();
                }
            });
            this.profileGroup = null;
        }

        // Create new dedicated instance for profile
        const { group, speed, rotationAxis } = this.createAvatarGroup(username, xp);
        this.profileGroup = group;
        this.profileScene.add(this.profileGroup);

        const animate = () => {
             if (canvas.offsetParent === null) {
                 this.profileRequestId = requestAnimationFrame(animate);
                 return;
             }

             this.profileRequestId = requestAnimationFrame(animate);

             const time = performance.now();

             // Rotation
             this.profileGroup.rotation.x = time * speed * rotationAxis.x * 0.1;
             this.profileGroup.rotation.y = time * speed * rotationAxis.y * 0.1;

             // Breathing Animation (GPU)
             this.profileGroup.traverse((child) => {
                 if (child.isMesh && child.material.uniforms) {
                     child.material.uniforms.uTime.value = time * 0.001;
                 }
             });

             this.profileRenderer.render(this.profileScene, this.profileCamera);
        };
        animate();
    }

    animate() {
        if (!this.isRunning) return;
        requestAnimationFrame(() => this.animate());

        if (!this.renderer || !this.container) return;
        if (document.hidden) return;

        this.renderer.setScissorTest(false);
        this.renderer.clear();
        this.renderer.setScissorTest(true);

        const time = performance.now();
        const timeSeconds = time * 0.001;

        // Iterate ONLY over visible avatars
        this.visibleAvatars.forEach(el => {
            const elRect = el.getBoundingClientRect();

            // Safety check (IntersectionObserver might have slight delay)
            if (elRect.bottom < 0 || elRect.top > window.innerHeight) return;

            const username = el.dataset.user;
            if (!username) return;

            const { group, speed, rotationAxis } = this.getMesh(username);

            // Animation
            group.rotation.x = time * speed * rotationAxis.x * 0.1;
            group.rotation.y = time * speed * rotationAxis.y * 0.1;

            // Breathing (GPU)
            group.traverse((child) => {
                 if (child.isMesh && child.material.uniforms) {
                     child.material.uniforms.uTime.value = timeSeconds;
                 }
            });

            this.scene.add(group);

            const width = elRect.width;
            const height = elRect.height;
            const left = elRect.left;
            const bottom = window.innerHeight - elRect.bottom;

            this.renderer.setViewport(left, bottom, width, height);
            this.renderer.setScissor(left, bottom, width, height);

            this.renderer.render(this.scene, this.camera);

            this.scene.remove(group);
        });

        this.renderer.setScissorTest(false);
    }
}

// Global instance
window.AvatarSystem = new SoulAvatarSystem();

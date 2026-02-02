
class SoulAvatarSystem {
    constructor() {
        this.canvas = document.getElementById('soul-avatars');
        this.renderer = null;
        this.container = document.getElementById('messages-container');
        this.isRunning = false;

        // Caches
        this.meshes = new Map(); // username -> { mesh, speed }

        // Single Shared Resources (Memory Optimization)
        this.scene = null;
        this.camera = null;
        this.sharedMaterial = null;
        this.baseGeometry = null;

        // Configuration
        this.baseColor = 0x6a4df4;
        this.secondaryColor = 0x74b9ff;

        // Profile Renderer State
        this.profileRenderer = null;
        this.profileScene = null;
        this.profileCamera = null;
        this.profileMesh = null;
        this.profileCanvas = null;
        this.profileRequestId = null;
    }

    init() {
        if (!this.canvas || !window.THREE) return;

        // Optimization: High Performance Mode
        this.renderer = new THREE.WebGLRenderer({
            canvas: this.canvas,
            alpha: true,
            antialias: true, // MSAA might be heavy, but needed for wireframes/thin lines.
            powerPreference: "high-performance",
            precision: "mediump" // optimization for mobile
        });

        this.renderer.setClearColor(0xffffff, 0); // Force transparency

        this.resize();
        window.addEventListener('resize', () => this.resize());

        // Setup Shared Scene
        this.scene = new THREE.Scene();
        this.camera = new THREE.PerspectiveCamera(50, 1, 0.1, 100);
        this.camera.position.z = 3.5;

        // Shared Lighting (Static)
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.4); // Reduced for better contrast
        this.scene.add(ambientLight);

        const pointLight = new THREE.PointLight(0xffffff, 1.2);
        pointLight.position.set(5, 5, 5);
        this.scene.add(pointLight);

        const pointLight2 = new THREE.PointLight(this.secondaryColor, 1.0);
        pointLight2.position.set(-5, -5, 2);
        this.scene.add(pointLight2);

        // Rim light for definition
        const pointLight3 = new THREE.PointLight(0xffffff, 1.0);
        pointLight3.position.set(0, 5, -5);
        this.scene.add(pointLight3);

        // Shared Material (Physical for "Liquid Glass" look)
        this.sharedMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xf0f8ff,   // AliceBlue (Slightly cool white)
            emissive: 0x004444, // Enhanced Cyan glow for visibility on white
            roughness: 0.05,   // Ultra Polished
            metalness: 0.2,    // Higher metalness for "Crystal" reflections
            transmission: 0.1, // Almost opaque to ensure it stands out against white
            thickness: 1.5,    // Volume
            clearcoat: 1.0,
            clearcoatRoughness: 0.05,
            ior: 1.7,          // High Index of Refraction (Crystal-like)
            side: THREE.FrontSide,
            flatShading: true // Faceted look for "Crystal" vibe
        });

        // Start animation loop
        this.isRunning = true;
        this.animate();
        console.log("Soul ID System Initialized (Optimized Mode)");
    }

    resize() {
        if (!this.renderer) return;
        const width = this.canvas.clientWidth;
        const height = this.canvas.clientHeight;
        if (this.canvas.width !== width || this.canvas.height !== height) {
            this.renderer.setSize(width, height, false);
            // Limit pixel ratio to 2 to prevent overheat on Retina screens
            this.renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
        }
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

    createGeometryData(username, xp) {
        const hash = this.stringToHash(username);

        // Determine complexity
        let layers = 0;
        if (xp >= 50) layers = 3;      // Complex Lotus
        else if (xp >= 21) layers = 2; // Blooming
        else if (xp >= 6) layers = 1;  // Bud/Simple
        else layers = 0;               // Seed

        // Reduced segments for faceted "Crystal" look with flatShading
        const geometry = new THREE.SphereGeometry(1, 32, 32);
        const positionAttribute = geometry.attributes.position;
        const vertex = new THREE.Vector3();

        let seed = hash;
        const random = () => {
            const x = Math.sin(seed++) * 10000;
            return x - Math.floor(x);
        };

        const petalFreq = 3 + Math.floor(random() * 4); // 3 to 6 petals
        const petalAmp = 0.2 + (random() * 0.3); // Depth of petals

        for (let i = 0; i < positionAttribute.count; i++) {
            vertex.fromBufferAttribute(positionAttribute, i);

            // Convert to spherical
            let r = vertex.length();
            let theta = Math.atan2(vertex.z, vertex.x);
            let phi = Math.acos(vertex.y / r);

            if (layers === 0) {
                // Level 0: Seed / Teardrop
                vertex.y *= 1.5; // Elongate
                // Taper logic: wider at bottom, narrower at top
                const yNorm = vertex.y / 1.5;
                const taper = 0.8 - 0.4 * yNorm;
                vertex.x *= taper;
                vertex.z *= taper;
            } else {
                // Level 1+: Lotus Petals
                let displacement = 0;

                // Base Petals
                displacement += Math.sin(theta * petalFreq) * Math.sin(phi * 3) * petalAmp;

                if (layers >= 2) {
                     // Inner/Offset Petals
                     displacement += Math.sin(theta * petalFreq * 1.5 + Math.PI) * Math.sin(phi * 5) * (petalAmp * 0.5);
                }

                if (layers >= 3) {
                     // Surface Texture/Detail
                     displacement += Math.sin(theta * 10) * Math.sin(phi * 10) * 0.05;
                }

                // Apply displacement
                r = 1.0 + Math.abs(displacement);

                // Reconstruct from spherical coordinates
                vertex.set(
                    r * Math.sin(phi) * Math.cos(theta),
                    r * Math.cos(phi),
                    r * Math.sin(phi) * Math.sin(theta)
                );
            }

            positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z);
        }

        geometry.computeVertexNormals();

        const baseSpeed = 0.002 + (xp * 0.0001); // Slower, more majestic

        return {
            geometry: geometry,
            speed: baseSpeed + (random() * 0.005),
            rotationAxis: new THREE.Vector3(random()-0.5, random()-0.5, random()-0.5).normalize()
        };
    }

    getMesh(username, xp = 0) {
        if (this.meshes.has(username)) {
            return this.meshes.get(username);
        }

        const { geometry, speed, rotationAxis } = this.createGeometryData(username, xp);
        const mesh = new THREE.Mesh(geometry, this.sharedMaterial);

        const data = {
            mesh: mesh,
            speed: speed,
            rotationAxis: rotationAxis
        };

        this.meshes.set(username, data);
        return data;
    }

    updateAvatar(username, xp) {
        if (this.meshes.has(username)) {
            const oldData = this.meshes.get(username);
            // Dispose old geometry
            if (oldData.mesh.geometry) oldData.mesh.geometry.dispose();
            this.meshes.delete(username);
        }
        // Force regeneration
        this.getMesh(username, xp);
    }

    renderProfileAvatar(canvas, username, xp) {
        if (!window.THREE) return;

        // Cancel old loop
        if (this.profileRequestId) {
            cancelAnimationFrame(this.profileRequestId);
            this.profileRequestId = null;
        }

        // Initialize Profile Renderer if needed
        if (!this.profileRenderer || this.profileCanvas !== canvas) {
            if (this.profileRenderer) {
                this.profileRenderer.dispose();
            }
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

            // Lights
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
            this.profileScene.add(ambientLight);

            const pointLight = new THREE.PointLight(0xffffff, 1.2);
            pointLight.position.set(5, 5, 5);
            this.profileScene.add(pointLight);

            const pointLight2 = new THREE.PointLight(this.secondaryColor, 1.0);
            pointLight2.position.set(-5, -5, 2);
            this.profileScene.add(pointLight2);

            const pointLight3 = new THREE.PointLight(0xffffff, 1.0);
            pointLight3.position.set(0, 5, -5);
            this.profileScene.add(pointLight3);
        }

        // Handle Resize based on CSS size (Initial)
        const width = canvas.clientWidth || 300; // Fallback to ensure render
        const height = canvas.clientHeight || 300;
        this.profileRenderer.setSize(width, height, false);
        this.profileCamera.aspect = width / height;
        this.profileCamera.updateProjectionMatrix();

        // Create/Update Mesh
        if (this.profileMesh) {
            this.profileScene.remove(this.profileMesh);
            if(this.profileMesh.geometry) this.profileMesh.geometry.dispose();
            this.profileMesh = null;
        }

        const { geometry, speed, rotationAxis } = this.createGeometryData(username, xp);
        this.profileMesh = new THREE.Mesh(geometry, this.sharedMaterial);
        this.profileScene.add(this.profileMesh);

        // Animation Loop
        const animate = () => {
             if (canvas.offsetParent === null) {
                 this.profileRequestId = requestAnimationFrame(animate);
                 return;
             }

             this.profileRequestId = requestAnimationFrame(animate);

             // Dynamic Resize
             const w = canvas.clientWidth;
             const h = canvas.clientHeight;
             if (w && h && (canvas.width !== w || canvas.height !== h)) {
                 this.profileRenderer.setSize(w, h, false);
                 this.profileCamera.aspect = w / h;
                 this.profileCamera.updateProjectionMatrix();
             }

             const time = performance.now();
             this.profileMesh.rotation.x = time * speed * rotationAxis.x * 0.1;
             this.profileMesh.rotation.y = time * speed * rotationAxis.y * 0.1;

             this.profileRenderer.render(this.profileScene, this.profileCamera);
        };
        animate();
    }

    animate() {
        if (!this.isRunning) return;
        requestAnimationFrame(() => this.animate());

        if (!this.renderer || !this.container) return;
        if (document.hidden) return;

        // 1. Clear Screen
        this.renderer.setScissorTest(false);
        this.renderer.clear();
        this.renderer.setScissorTest(true);

        const placeholders = document.querySelectorAll('.soul-avatar-placeholder');

        // Optimization: Iterate placeholders
        for (let i = 0; i < placeholders.length; i++) {
            const el = placeholders[i];
            const elRect = el.getBoundingClientRect();

            // Frustum Culling
            if (elRect.bottom < 0 || elRect.top > window.innerHeight) continue;

            const username = el.dataset.user;
            if (!username) continue;

            const { mesh, speed, rotationAxis } = this.getMesh(username);

            // Animation (Time-based to avoid speedup on multiple instances)
            const time = performance.now();
            mesh.rotation.x = time * speed * rotationAxis.x * 0.1;
            mesh.rotation.y = time * speed * rotationAxis.y * 0.1;

            // Render Logic (Single Scene Swap)
            // Add mesh to shared scene -> Render -> Remove
            this.scene.add(mesh);

            const width = elRect.width;
            const height = elRect.height;
            const left = elRect.left;
            const bottom = window.innerHeight - elRect.bottom; // WebGL uses bottom-left origin

            this.renderer.setViewport(left, bottom, width, height);
            this.renderer.setScissor(left, bottom, width, height);

            this.renderer.render(this.scene, this.camera);

            this.scene.remove(mesh);
        }

        this.renderer.setScissorTest(false);
    }
}

// Global instance
const AvatarSystem = new SoulAvatarSystem();

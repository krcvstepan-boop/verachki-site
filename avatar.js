
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

        // Shared Material (Physical Glass / Crystal)
        this.sharedMaterial = new THREE.MeshPhysicalMaterial({
            color: 0xffffff,
            transmission: 1.0,
            roughness: 0.05,
            thickness: 1.5,
            ior: 1.5,
            transparent: true,
            side: THREE.FrontSide,
            flatShading: false
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

        // High-segment sphere for organic glass look
        const geometry = new THREE.SphereGeometry(1, 64, 64);
        const positionAttribute = geometry.attributes.position;
        const vertex = new THREE.Vector3();

        let seed = hash;
        const random = () => {
            const x = Math.sin(seed++) * 10000;
            return x - Math.floor(x);
        };

        // Petal Algorithm
        const petals = 5 + Math.floor(random() * 2); // 5 or 6 petals
        const amplitude = 0.1 + (Math.min(xp, 100) * 0.002); // Grows slightly with XP

        for (let i = 0; i < positionAttribute.count; i++) {
            vertex.fromBufferAttribute(positionAttribute, i);

            // Calculate spherical coordinates approximation
            const angle = Math.atan2(vertex.z, vertex.x);
            const elevation = vertex.y;

            // Soft overlapping curves displacement
            const displacement = 1.0 + amplitude *
                                       Math.sin(petals * angle + seed) *
                                       Math.cos(3 * elevation);

            vertex.multiplyScalar(displacement);
            positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z);
        }

        geometry.computeVertexNormals();

        const baseSpeed = 0.005 + (xp * 0.0001);

        return {
            geometry: geometry,
            speed: baseSpeed + (random() * 0.01),
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
            const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
            this.profileScene.add(ambientLight);
            const pointLight = new THREE.PointLight(0xffffff, 1);
            pointLight.position.set(5, 5, 5);
            this.profileScene.add(pointLight);
            const pointLight2 = new THREE.PointLight(this.secondaryColor, 0.8);
            pointLight2.position.set(-5, -5, 2);
            this.profileScene.add(pointLight2);
        }

        // Handle Resize based on CSS size
        const width = canvas.clientWidth;
        const height = canvas.clientHeight;
        if (canvas.width !== width || canvas.height !== height) {
             this.profileRenderer.setSize(width, height, false);
             this.profileCamera.aspect = width / height;
             this.profileCamera.updateProjectionMatrix();
        }

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

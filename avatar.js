
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

        // Shared Material (Phong is faster and handles simple lights better for "fake glass")
        this.sharedMaterial = new THREE.MeshPhongMaterial({
            color: 0xffffff,
            emissive: 0x111111,
            specular: 0xffffff,
            shininess: 100,
            transparent: true,
            opacity: 0.7,
            side: THREE.FrontSide,
            flatShading: true // Enhances the "fractal/crystal" look
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

    getMesh(username) {
        if (this.meshes.has(username)) {
            return this.meshes.get(username);
        }

        const hash = this.stringToHash(username);

        // Generate Unique Geometry
        const detail = 1; // 80 faces
        const geometry = new THREE.IcosahedronGeometry(1, detail);
        const positionAttribute = geometry.attributes.position;
        const vertex = new THREE.Vector3();

        // Deterministic RNG based on hash
        let seed = hash;
        const random = () => {
            const x = Math.sin(seed++) * 10000;
            return x - Math.floor(x);
        };

        // Displace vertices to create "Fractal/Spike" look
        // Done once on CPU (lightweight enough for <100 users)
        for (let i = 0; i < positionAttribute.count; i++) {
            vertex.fromBufferAttribute(positionAttribute, i);
            const spikeFactor = 1.0 + (random() * 0.6);
            vertex.multiplyScalar(spikeFactor);
            positionAttribute.setXYZ(i, vertex.x, vertex.y, vertex.z);
        }

        geometry.computeVertexNormals();

        const mesh = new THREE.Mesh(geometry, this.sharedMaterial);

        const data = {
            mesh: mesh,
            speed: 0.005 + (random() * 0.01),
            rotationAxis: new THREE.Vector3(random()-0.5, random()-0.5, random()-0.5).normalize()
        };

        this.meshes.set(username, data);
        return data;
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

            // Animation
            mesh.rotation.x += speed * rotationAxis.x * 2;
            mesh.rotation.y += speed * rotationAxis.y * 2;

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

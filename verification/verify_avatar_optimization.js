const fs = require('fs');
const path = require('path');

// --- Mock Browser Environment ---

// Mock THREE.js
const THREE = {
    WebGLRenderer: class {
        constructor() {}
        setClearColor() {}
        setSize() {}
        setPixelRatio() {}
        setScissorTest() {}
        clear() {}
        setViewport() {}
        setScissor() {}
        render() {}
        dispose() {}
    },
    Scene: class { add() {} remove() {} },
    PerspectiveCamera: class { constructor() { this.position = { z: 0, set: () => {} }; } updateProjectionMatrix() {} },
    AmbientLight: class { constructor() {} },
    PointLight: class { constructor() { this.position = { set: () => {} }; } },
    Group: class {
        constructor() { this.children = []; this.isGroup = true; }
        add(child) { this.children.push(child); }
        traverse(cb) { this.children.forEach(c => cb(c)); }
        rotation = { x: 0, y: 0, set: () => {} };
        scale = { setScalar: () => {} };
    },
    SphereGeometry: class {
        constructor() {
            this.attributes = {
                position: { count: 10, fromBufferAttribute: () => {}, setXYZ: () => {} }
            };
        }
        computeVertexNormals() {}
        dispose() {}
    },
    Vector3: class {
        constructor(x,y,z) { this.x=x; this.y=y; this.z=z; }
        normalize() { return this; }
        multiplyScalar() {}
        fromBufferAttribute() {}
    },
    ShaderMaterial: class { constructor() { this.uniforms = { uTime: { value: 0 } }; } dispose() {} },
    Mesh: class {
        constructor(g, m) { this.isMesh = true; this.material = m || { uniforms: { uTime: { value: 0 } } }; this.geometry = g; }
        rotation = { set: () => {} };
        scale = { setScalar: () => {} };
    },
    BufferGeometry: class { setAttribute() {} },
    BufferAttribute: class {},
    PointsMaterial: class {},
    Points: class {},
    Color: class {},
    Math: { degToRad: () => {} }
};

// Mock Window & Document
global.window = {
    THREE: THREE,
    addEventListener: () => {},
    devicePixelRatio: 1,
    innerHeight: 1000,
    innerWidth: 1000,
    requestAnimationFrame: (cb) => {
        if (!global.window._rafCount) global.window._rafCount = 0;
        if (global.window._rafCount < 5) { // Limit frames
            global.window._rafCount++;
            setTimeout(cb, 16);
        }
        return 1;
    },
    cancelAnimationFrame: () => {},
    setTimeout: setTimeout,
    document: null // Will be set below
};

global.document = {
    getElementById: (id) => {
        if (id === 'soul-avatars') return { clientWidth: 100, clientHeight: 100, width: 100, height: 100 };
        if (id === 'messages-container') return {
            clientWidth: 100, clientHeight: 100,
            appendChild: () => {},
            addEventListener: () => {},
            querySelectorAll: () => []
        };
        return { clientWidth: 100, clientHeight: 100 };
    },
    querySelectorAll: (sel) => {
        console.log(`[AUDIT] querySelectorAll called with "${sel}"`);
        // Return mock NodeList
        const el = {
            dataset: { user: 'testUser' },
            getBoundingClientRect: () => ({ top: 10, bottom: 90, left: 10, right: 90, width: 80, height: 80 }),
            isConnected: true
        };
        return [el];
    },
    createElement: () => ({ style: {} }),
    body: { appendChild: () => {} },
    hidden: false
};
global.window.document = global.document;

global.performance = { now: () => Date.now() };

// Mock Observers
global.IntersectionObserver = class {
    constructor(cb) { this.cb = cb; }
    observe(el) {
        // Simulate immediate intersection
        this.cb([{ target: el, isIntersecting: true, boundingClientRect: el.getBoundingClientRect() }]);
    }
    disconnect() {}
    unobserve() {}
};

global.MutationObserver = class {
    constructor(cb) { this.cb = cb; }
    observe() {}
    disconnect() {}
};

// Make globals available for eval
const window = global.window;
const document = global.document;
const performance = global.performance;
const IntersectionObserver = global.IntersectionObserver;
const MutationObserver = global.MutationObserver;
const requestAnimationFrame = global.window.requestAnimationFrame;
const cancelAnimationFrame = global.window.cancelAnimationFrame;

// Load and Run avatar.js
const avatarPath = path.join(__dirname, '../avatar.js');
const code = fs.readFileSync(avatarPath, 'utf8');

console.log("--- Loading avatar.js ---");
try {
    eval(code);
} catch (e) {
    console.error("Error loading avatar.js:", e);
    process.exit(1);
}

// Run Test
console.log("--- Initializing System ---");
if (window.AvatarSystem) {
    window.AvatarSystem.init();

    // Reset RAF count to allow animation loop to run a few times
    window._rafCount = 0;

    console.log("--- Starting Animation Loop ---");

    // We wait a bit for async operations (setTimeout in RAF mock)
    setTimeout(() => {
        console.log("--- Test Complete ---");
    }, 200);
} else {
    console.error("AvatarSystem not found on window object.");
}

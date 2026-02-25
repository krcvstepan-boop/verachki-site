const fs = require('fs');
const path = require('path');

// Mock Browser Environment
global.window = {
    innerWidth: 1024,
    innerHeight: 768,
    devicePixelRatio: 1,
    addEventListener: () => {},
    removeEventListener: () => {},
    requestAnimationFrame: (cb) => { return 1; }, // Mock RAF - No auto execution
    cancelAnimationFrame: (id) => {},
    setTimeout: setTimeout,
    clearTimeout: clearTimeout,
    performance: { now: () => Date.now() }
};

global.document = {
    getElementById: (id) => {
        if (id === 'soul-avatars') return { width: 1024, height: 768, clientWidth: 1024, clientHeight: 768, getContext: () => {} };
        if (id === 'messages-container') return { querySelectorAll: () => [], appendChild: () => {} };
        return null;
    },
    querySelectorAll: () => [], // Spy target
    createElement: (tag) => {
        return {
            tagName: tag.toUpperCase(),
            style: {},
            classList: { add: () => {}, remove: () => {} },
            appendChild: () => {},
            dataset: {},
            getBoundingClientRect: () => ({ top: 0, left: 0, width: 100, height: 100, bottom: 100 })
        };
    },
    hidden: false
};

global.HTMLElement = class {};
global.requestAnimationFrame = global.window.requestAnimationFrame;
global.cancelAnimationFrame = global.window.cancelAnimationFrame;
global.performance = global.window.performance;

// Mock THREE.js (Minimal)
global.THREE = {
    WebGLRenderer: class {
        constructor() { this.domElement = {}; }
        setSize() {}
        setPixelRatio() {}
        setClearColor() {}
        setScissorTest() {}
        clear() {}
        setViewport() {}
        setScissor() {}
        render() {}
        dispose() {}
    },
    Scene: class { add() {} remove() {} },
    PerspectiveCamera: class { position = { z: 0 }; aspect = 1; updateProjectionMatrix() {} },
    AmbientLight: class {},
    PointLight: class { position = { set: () => {} }; },
    Group: class { add() {} remove() {} traverse() {} rotation = { x: 0, y: 0 }; scale = { setScalar: () => {} }; },
    SphereGeometry: class { attributes = { position: { count: 0, fromBufferAttribute: () => {}, setXYZ: () => {} } }; computeVertexNormals() {} dispose() {} },
    Vector3: class { fromBufferAttribute() {} multiplyScalar() {} normalize() { return this; } },
    ShaderMaterial: class { dispose() {} },
    Mesh: class { rotation = { set: () => {} }; scale = { setScalar: () => {} }; },
    BufferGeometry: class { setAttribute() {} },
    BufferAttribute: class {},
    PointsMaterial: class {},
    Points: class {},
    Color: class {},
    Math: {
        degToRad: (d) => d * Math.PI / 180
    }
};
global.window.THREE = global.THREE;

// Mock Observers
global.IntersectionObserver = class {
    constructor(callback) {
        this.callback = callback;
    }
    observe(el) {
        // Simulate immediate intersection for testing
        this.callback([{ target: el, isIntersecting: true }]);
    }
    unobserve(el) {
        this.callback([{ target: el, isIntersecting: false }]);
    }
    disconnect() {}
};

global.MutationObserver = class {
    constructor(callback) {
        this.callback = callback;
    }
    observe() {}
    disconnect() {}
};

// Load Avatar System
const avatarScript = fs.readFileSync(path.join(__dirname, '../avatar.js'), 'utf8');
eval(avatarScript);

// Verification Logic
async function verify() {
    console.log("Verifying Avatar Optimization...");

    if (!window.AvatarSystem) {
        console.error("AvatarSystem not found!");
        process.exit(1);
    }

    // Mock DOM elements for test
    const container = {
        querySelectorAll: () => [],
        appendChild: () => {}
    };
    const canvas = {
        clientWidth: 1024,
        clientHeight: 768,
        width: 1024,
        height: 768,
        style: {},
        getContext: () => ({})
    };

    // Override document.getElementById for our test instance
    const originalGetElementById = document.getElementById;
    document.getElementById = (id) => {
        if (id === 'messages-container') return container;
        if (id === 'soul-avatars') return canvas;
        return originalGetElementById(id);
    };

    const system = window.AvatarSystem;

    // Inject mock renderer if not present (constructor might have failed if canvas missing)
    if (!system.renderer) {
        system.renderer = new THREE.WebGLRenderer();
        system.scene = new THREE.Scene();
        system.camera = new THREE.PerspectiveCamera();
        system.canvas = document.getElementById('soul-avatars');
        system.container = document.getElementById('messages-container');
    }

    // Spy on querySelectorAll
    let querySelectorAllCallCount = 0;
    document.querySelectorAll = (selector) => {
        if (selector === '.soul-avatar-placeholder') {
            querySelectorAllCallCount++;
            // Return fake NodeList
            return [
                { getBoundingClientRect: () => ({ top: 100, bottom: 200, left: 0, width: 50, height: 50 }), dataset: { user: 'test' } }
            ];
        }
        return [];
    };

    // Spy on getBoundingClientRect inside the loop
    // But since we mock the return of querySelectorAll, the elements themselves are spies.

    system.init();

    // Force one animation frame
    system.animate();

    console.log(`Initial render call count for querySelectorAll: ${querySelectorAllCallCount}`);

    // Expectation: querySelectorAll SHOULD be called in current implementation
    // After optimization, it should be called 0 times (or maybe once during init, but not during animate loop)
    // We are testing the LOOP here.

    // Reset count and call animate again
    querySelectorAllCallCount = 0;
    system.animate();

    if (querySelectorAllCallCount > 0) {
        console.log("FAIL: querySelectorAll is still being called in animate loop!");
        // For now, this is expected behavior of the OLD code.
        // Once optimized, we expect this to be 0.
    } else {
        console.log("SUCCESS: querySelectorAll was NOT called in animate loop.");
    }

    // Check if visibleAvatars logic is working (if implemented)
    if (system.visibleAvatars) {
        console.log(`Visible Avatars Count: ${system.visibleAvatars.size}`);
        if (system.visibleAvatars.size > 0 && querySelectorAllCallCount === 0) {
             console.log("OPTIMIZATION VERIFIED: Using visibleAvatars set.");
        }
    } else {
        console.log("Optimization not yet implemented (no visibleAvatars Set).");
    }

}

verify();

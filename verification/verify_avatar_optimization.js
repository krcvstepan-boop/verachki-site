
const fs = require('fs');
const path = require('path');

// --- MOCKING ---

// Simple spy implementation
function createSpy(impl = () => []) {
    const fn = function(...args) {
        console.log("Spy called with:", args);
        fn.mock.calls.push(args);
        return impl(...args);
    };
    fn.mock = { calls: [] };
    fn.mockClear = () => { fn.mock.calls = []; };
    return fn;
}

global.window = {
    addEventListener: () => {},
    innerWidth: 1024,
    innerHeight: 768,
    devicePixelRatio: 1,
    AvatarSystem: null,
    requestAnimationFrame: (cb) => {}
};

global.document = {
    getElementById: (id) => {
        if (id === 'soul-avatars') return { clientWidth: 100, clientHeight: 100, width: 100, height: 100 };
        if (id === 'messages-container') return { querySelectorAll: () => [] };
        return {};
    },
    querySelectorAll: createSpy(), // Spy on this
    hidden: false
};

global.HTMLElement = class {};
global.requestAnimationFrame = (cb) => {};
global.performance = { now: () => 0 };

// Mock THREE
global.THREE = {
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
    PerspectiveCamera: class { constructor() { this.position = { z: 0 }; } },
    AmbientLight: class {},
    PointLight: class { constructor() { this.position = { set: () => {} }; } },
    Group: class { constructor() { this.add = () => {}; this.traverse = () => {}; this.rotation = { set: () => {} }; this.scale = { setScalar: () => {} }; } },
    SphereGeometry: class {
        constructor() {
            this.attributes = { position: { count: 0, fromBufferAttribute: () => {}, setXYZ: () => {} } };
            this.computeVertexNormals = () => {};
            this.dispose = () => {};
        }
    },
    Vector3: class {
        constructor(x=0, y=0, z=0) { this.x=x; this.y=y; this.z=z; }
        fromBufferAttribute() {}
        multiplyScalar() {}
        normalize() { return this; }
    },
    ShaderMaterial: class { constructor() { this.dispose = () => {}; } },
    Mesh: class { constructor() { this.rotation = { set: () => {} }; this.scale = { setScalar: () => {} }; } },
    BufferGeometry: class { setAttribute() {} dispose() {} },
    BufferAttribute: class {},
    PointsMaterial: class { dispose() {} },
    Points: class {},
    Color: class {},
    FrontSide: 0,
    AdditiveBlending: 0
};

// Bind THREE to window
global.window.THREE = global.THREE;

// Mock Observers
global.IntersectionObserver = class {
    constructor(cb) { this.cb = cb; }
    observe() {}
    unobserve() {}
    disconnect() {}
};

global.MutationObserver = class {
    constructor(cb) { this.cb = cb; }
    observe() {}
    disconnect() {}
};

// Load and Execute avatar.js
const avatarCode = fs.readFileSync(path.join(__dirname, '../avatar.js'), 'utf8');

try {
    // Wrap in function to avoid const redeclaration issues if run multiple times (though here run once)
    // But `avatar.js` relies on `window.AvatarSystem` assignment.
    // And it has `const vertexShader`.
    // Simple eval should work for one run.
    eval(avatarCode);
} catch (e) {
    console.error("Error evaluating avatar.js:", e);
    process.exit(1);
}

// Test
function runTest() {
    if (!global.window.AvatarSystem) {
        console.error("AvatarSystem not initialized");
        return;
    }

    // Init
    console.log("Initializing AvatarSystem...");
    global.window.AvatarSystem.init();

    // Inspect
    console.log("Instance state:", {
        isRunning: global.window.AvatarSystem.isRunning,
        renderer: !!global.window.AvatarSystem.renderer,
        container: !!global.window.AvatarSystem.container,
        documentHidden: global.document.hidden
    });

    // Reset spy
    console.log("Clearing spy...");
    global.document.querySelectorAll.mockClear();

    // Animate
    console.log("Running animate()...");
    global.window.AvatarSystem.animate();

    const calls = global.document.querySelectorAll.mock.calls;
    console.log(`document.querySelectorAll called ${calls.length} times.`);

    if (calls.length > 0) {
        // Check if called with .soul-avatar-placeholder
        const relevantCalls = calls.filter(args => args[0] === '.soul-avatar-placeholder');

        if (relevantCalls.length > 0) {
            console.log("FAIL: document.querySelectorAll('.soul-avatar-placeholder') was called.");
            process.exit(1);
        } else {
            console.log("PASS: document.querySelectorAll('.soul-avatar-placeholder') was NOT called.");
        }
    } else {
        console.log("PASS: document.querySelectorAll was NOT called.");
    }

    // Verify Logic
    console.log("Verifying Logic...");
    const system = global.window.AvatarSystem;

    // Simulate Intersection
    const mockElement = {
        getBoundingClientRect: () => ({ top: 100, bottom: 200, left: 0, width: 100, height: 100 }),
        dataset: { user: 'testuser' },
        style: {}
    };

    // Manually trigger IO callback
    const ioCallback = system.io.cb;
    ioCallback([{ target: mockElement, isIntersecting: true }]);

    if (system.visibleAvatars.has(mockElement)) {
        console.log("PASS: Element added to visibleAvatars.");
    } else {
        console.log("FAIL: Element NOT added to visibleAvatars.");
        process.exit(1);
    }

    // Run animate again
    system.animate();

    // Logic check: animate calls getBoundingClientRect on visible elements
    // But mockElement.getBoundingClientRect is not a spy.
    // Let's spy it.

}

runTest();

const fs = require('fs');
const path = require('path');

// --- Mock Browser Environment ---
global.window = {
    innerWidth: 1000,
    innerHeight: 800,
    devicePixelRatio: 1,
    addEventListener: () => {},
    removeEventListener: () => {},
    cancelAnimationFrame: () => {},
    requestAnimationFrame: (cb) => {
        return 1;
    },
    setTimeout: setTimeout,
    AvatarSystem: null,
};
global.window.THREE = {}; // Placeholder

global.document = {
    getElementById: (id) => {
        if (id === 'soul-avatars') return { clientWidth: 1000, clientHeight: 800, width: 1000, height: 800, style: {} };
        if (id === 'messages-container') return {
            appendChild: () => {},
            querySelectorAll: () => [],
            addEventListener: () => {}
        };
        return null;
    },
    querySelectorAll: () => { return []; },
    createElement: () => ({ style: {}, dataset: {} }),
    hidden: false,
    body: { appendChild: () => {} }
};

global.HTMLElement = class {};

// Mock IntersectionObserver
global.IntersectionObserver = class {
    constructor(cb) { this.cb = cb; }
    observe(el) {
        this.cb([{ isIntersecting: true, target: el }]);
    }
    unobserve() {}
    disconnect() {}
};

// Mock MutationObserver
global.MutationObserver = class {
    constructor(cb) { this.cb = cb; }
    observe() {}
    disconnect() {}
};

global.requestAnimationFrame = global.window.requestAnimationFrame;
global.cancelAnimationFrame = global.window.cancelAnimationFrame;

// --- Mock THREE.js ---
global.THREE = {
    WebGLRenderer: class {
        constructor() {
            this.domElement = {};
        }
        setSize() {}
        setPixelRatio() {}
        setClearColor() {}
        render() {}
        setScissorTest() {}
        clear() {}
        setViewport() {}
        setScissor() {}
        dispose() {}
    },
    Scene: class { add() {} remove() {} },
    PerspectiveCamera: class { position = { z: 0 }; updateProjectionMatrix() {} },
    AmbientLight: class {},
    PointLight: class { position = { set: () => {} }; },
    Group: class {
        add() {}
        remove() {}
        traverse() {}
        rotation = { set: () => {}, x: 0, y: 0 };
        scale = { setScalar: () => {} };
    },
    SphereGeometry: class {
        attributes = { position: { count: 10, setXYZ: () => {} }, normal: { count: 10 } };
        computeVertexNormals() {}
        dispose() {}
    },
    Vector3: class { fromBufferAttribute() {} multiplyScalar() {} set() {} normalize() { return this; } },
    ShaderMaterial: class { dispose() {} },
    Mesh: class { rotation = { set: () => {} }; scale = { setScalar: () => {} }; },
    Color: class {},
    BufferGeometry: class { setAttribute() {} dispose() {} },
    BufferAttribute: class {},
    PointsMaterial: class { dispose() {} },
    Points: class {},
    Math: {
        degToRad: (deg) => deg * Math.PI / 180,
    },
    FrontSide: 0,
    AdditiveBlending: 1
};

global.window.THREE = global.THREE;

// --- Load avatar.js ---
const avatarCode = fs.readFileSync(path.join(__dirname, '../avatar.js'), 'utf8');
eval(avatarCode);

// --- Verification Logic ---
async function verify() {
    console.log("Verifying AvatarSystem optimization...");

    const SystemClass = global.window.AvatarSystem.constructor;
    const system = new SystemClass();

    // Setup mocks
    system.canvas = global.document.getElementById('soul-avatars');
    system.container = global.document.getElementById('messages-container');

    let querySelectorAllCalls = 0;
    const originalQSA = global.document.querySelectorAll;

    // Override QSA
    global.document.querySelectorAll = (selector) => {
        if (selector === '.soul-avatar-placeholder') {
            console.log("Captured QSA call for placeholders");
            querySelectorAllCalls++;
            return [];
        }
        return originalQSA(selector);
    };

    console.log("Initializing system...");
    system.init();

    // Reset counter because init() calls QSA once (this is expected and good)
    console.log(`QSA calls during init: ${querySelectorAllCalls}`);
    querySelectorAllCalls = 0;

    console.log("Running animate...");
    system.animate();

    console.log(`querySelectorAll calls during animate: ${querySelectorAllCalls}`);

    if (querySelectorAllCalls > 0) {
        console.log("FAIL: querySelectorAll was called during animation loop.");
    } else {
        console.log("SUCCESS: querySelectorAll was NOT called during animation loop.");
    }

    // Verify visibleAvatars
    if (system.visibleAvatars instanceof Set) {
        console.log("SUCCESS: visibleAvatars Set exists.");
    } else {
        console.log("FAIL: visibleAvatars Set missing.");
    }
}

verify();

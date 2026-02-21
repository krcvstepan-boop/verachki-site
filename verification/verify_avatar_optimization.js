
const fs = require('fs');
const path = require('path');

// --- Mocks ---

global.window = {
    innerWidth: 1024,
    innerHeight: 768,
    devicePixelRatio: 1,
    addEventListener: () => {},
    THREE: null // Will be set later
};

global.document = {
    getElementById: (id) => {
        if (id === 'soul-avatars') return { clientWidth: 800, clientHeight: 600, width: 800, height: 600 };
        if (id === 'messages-container') return {
            appendChild: () => {},
            addEventListener: () => {}
        };
        return null;
    },
    querySelectorAll: () => [], // Spy target
    hidden: false,
    body: {}
};

global.HTMLElement = class {};

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

global.requestAnimationFrame = (cb) => {
    // Store callback to run later if needed, or just ignore for single-step verification
    return 1;
};

global.cancelAnimationFrame = () => {};

global.performance = { now: () => Date.now() };

// Mock THREE
const THREE = {
    WebGLRenderer: class {
        constructor() { this.domElement = {}; }
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
    PointLight: class { setPosition() {} set() {} constructor() { this.position = { set: () => {} }; } },
    Group: class { constructor() { this.rotation = { x: 0, y: 0 }; this.add = () => {}; this.traverse = () => {}; } },
    SphereGeometry: class { constructor() { this.attributes = { position: { count: 0 } }; this.computeVertexNormals = () => {}; } },
    ShaderMaterial: class {},
    Mesh: class { constructor() { this.rotation = { set: () => {} }; this.scale = { setScalar: () => {} }; } },
    BufferGeometry: class { setAttribute() {} },
    BufferAttribute: class {},
    PointsMaterial: class {},
    Points: class {},
    Vector3: class { constructor() { this.x=0; this.y=0; this.z=0; } normalize() { return this; } },
    Color: class {},
    FrontSide: 1,
    AdditiveBlending: 2
};
global.window.THREE = THREE;
global.THREE = THREE; // For direct access if needed

// --- Test ---

const avatarJsPath = path.join(__dirname, '../avatar.js');
const avatarJsContent = fs.readFileSync(avatarJsPath, 'utf8');

// Spy on querySelectorAll
let querySelectorAllCallCount = 0;
const originalQuerySelectorAll = global.document.querySelectorAll;
global.document.querySelectorAll = (selector) => {
    if (selector === '.soul-avatar-placeholder') {
        querySelectorAllCallCount++;
    }
    return []; // Return empty list for now
};

console.log("Loading avatar.js...");
eval(avatarJsContent);

console.log("Initializing AvatarSystem...");
if (typeof window.AvatarSystem === 'undefined') {
    console.error("AvatarSystem not found on window!");
    process.exit(1);
}

const system = window.AvatarSystem;
system.init();

// Reset spy count (init might call it in optimized version)
const initCallCount = querySelectorAllCallCount;
querySelectorAllCallCount = 0;

console.log("Running animate()...");
// We need to trigger animate. animate() calls requestAnimationFrame.
// We mocked requestAnimationFrame to do nothing, so we call system.animate() manually once.
system.animate();

console.log(`querySelectorAll called ${querySelectorAllCallCount} times in animate().`);

if (querySelectorAllCallCount > 0) {
    console.log("Current state: UNOPTIMIZED (calls querySelectorAll)");
} else {
    // Check if visibleAvatars exists
    if (system.visibleAvatars instanceof Set) {
        console.log("Current state: OPTIMIZED (uses visibleAvatars)");
    } else {
         console.log("Current state: BROKEN? (No querySelectorAll but no visibleAvatars)");
    }
}

// Verification Logic for future run
if (process.argv.includes('--verify-optimized')) {
    if (querySelectorAllCallCount === 0 && system.visibleAvatars instanceof Set) {
        console.log("PASS: Optimization verified.");
        process.exit(0);
    } else {
        console.error("FAIL: Optimization NOT verified.");
        if (querySelectorAllCallCount > 0) console.error(" - querySelectorAll still called.");
        if (!(system.visibleAvatars instanceof Set)) console.error(" - visibleAvatars Set missing.");
        process.exit(1);
    }
} else {
    // Verification logic for initial run (expect unoptimized)
     if (querySelectorAllCallCount > 0) {
        console.log("PASS: Baseline confirmed (Unoptimized).");
        process.exit(0);
    } else {
        console.warn("WARN: Baseline unexpected (Already optimized?).");
        process.exit(0);
    }
}

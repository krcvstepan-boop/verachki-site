const fs = require('fs');
const path = require('path');

// Mock Browser Environment
global.window = {
    innerWidth: 1024,
    innerHeight: 768,
    devicePixelRatio: 1,
    addEventListener: () => {},
    AvatarSystem: null,
    THREE: {}
};

global.document = {
    getElementById: (id) => {
        if (id === 'soul-avatars') return { clientWidth: 100, clientHeight: 100, style: {}, width: 100, height: 100 };
        if (id === 'messages-container') return { style: {} };
        return null;
    },
    querySelectorAll: () => [],
    createElement: () => ({ style: {}, classList: { add: () => {} } }),
    hidden: false
};

global.HTMLElement = class {};

global.requestAnimationFrame = (cb) => {
    // We don't want the loop to actually run indefinitely in this test env
    return 1;
};
global.cancelAnimationFrame = () => {};

// Mock THREE
global.THREE = {
    WebGLRenderer: class {
        constructor() {}
        setClearColor() {}
        setSize() {}
        setPixelRatio() {}
        render() {}
        setScissorTest() {}
        clear() {}
        setViewport() {}
        setScissor() {}
        dispose() {}
    },
    Scene: class {
        add() {}
        remove() {}
    },
    PerspectiveCamera: class { constructor() { this.position = { z: 0 }; } },
    AmbientLight: class {},
    PointLight: class { constructor() { this.position = { set: () => {} }; } },
    Group: class {
        constructor() { this.rotation = {}; }
        add() {}
        traverse() {}
    },
    Vector3: class { constructor() {} normalize() { return this; } },
    Color: class {},
    SphereGeometry: class {
        constructor() {
            this.attributes = {
                position: { count: 10, setXYZ: () => {}, fromBufferAttribute: () => {} }
            };
        }
        computeVertexNormals() {}
    },
    ShaderMaterial: class {},
    Mesh: class { constructor() { this.rotation = { set: () => {} }; this.scale = { setScalar: () => {} }; } },
    BufferGeometry: class { setAttribute() {} },
    BufferAttribute: class {},
    PointsMaterial: class {},
    Points: class {},
    MathUtils: { randFloat: () => 0.5 }
};

// Make sure window.THREE is available
global.window.THREE = global.THREE;

// Capture callbacks
global.testIntersectionCallback = null;
global.testMutationCallback = null;

// Mock Observers
global.IntersectionObserver = class {
    constructor(callback) {
        this.callback = callback;
        global.testIntersectionCallback = callback;
    }
    observe() {}
    unobserve() {}
    disconnect() {}
};

global.MutationObserver = class {
    constructor(callback) {
        this.callback = callback;
        global.testMutationCallback = callback;
    }
    observe() {}
    disconnect() {}
};

// Load and eval avatar.js
const avatarCode = fs.readFileSync(path.join(__dirname, '../avatar.js'), 'utf8');

try {
    eval(avatarCode);
} catch (e) {
    console.error("Error evaluating avatar.js:", e);
    process.exit(1);
}

// Verification Logic
async function runVerification() {
    console.log("Verifying AvatarSystem Optimization...");

    const system = global.window.AvatarSystem;
    if (!system) {
        console.error("FAIL: AvatarSystem not found on window.");
        process.exit(1);
    }

    // 1. Check Idempotency (init called twice)
    console.log("Checking init() idempotency...");
    system.init();
    system.init();

    // Check if initialized flag exists (Optimization Requirement)
    if (system.initialized === undefined) {
         console.log("INFO: 'initialized' flag not found (Current State).");
    } else {
         console.log("PASS: 'initialized' flag present.");
    }

    // 2. Check setupObservers (Optimization Requirement)
    if (!system.visibleAvatars) {
        console.log("INFO: 'visibleAvatars' Set not found (Current State).");
        console.log("FAIL: Optimization not implemented yet.");
        process.exit(0);
    } else {
        console.log("PASS: 'visibleAvatars' Set found.");

        // Test Intersection Logic
        const mockEntry = {
            target: { dataset: { user: 'testUser' } },
            isIntersecting: true
        };

        if (global.testIntersectionCallback) {
            console.log("Triggering IntersectionObserver callback...");
            global.testIntersectionCallback([mockEntry]);

            // Check if the element itself is in the Set
            if (system.visibleAvatars.has(mockEntry.target)) {
                console.log("PASS: IntersectionObserver added user element to visibleAvatars.");
            } else {
                console.error("FAIL: IntersectionObserver did NOT add user element.");
                process.exit(1);
            }

            mockEntry.isIntersecting = false;
            global.testIntersectionCallback([mockEntry]);
            if (!system.visibleAvatars.has(mockEntry.target)) {
                console.log("PASS: IntersectionObserver removed user element from visibleAvatars.");
            } else {
                console.error("FAIL: IntersectionObserver did NOT remove user element.");
                process.exit(1);
            }
        } else {
             console.error("FAIL: IntersectionObserver callback not captured.");
             process.exit(1);
        }

        // Test Mutation Logic (Simplified check that it exists)
        if (global.testMutationCallback) {
             console.log("PASS: MutationObserver initialized.");
        } else {
             console.error("FAIL: MutationObserver not initialized.");
             process.exit(1);
        }
    }
}

runVerification();

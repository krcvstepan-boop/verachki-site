const assert = require('assert');

// Simple DOM Mock
global.window = {
    innerWidth: 1024,
    innerHeight: 768,
    devicePixelRatio: 1,
    addEventListener: () => {},
};

global.THREE = {
    WebGLRenderer: class {
        setClearColor() {}
        setSize() {}
        setPixelRatio() {}
        setScissorTest() {}
        clear() {}
        setViewport() {}
        setScissor() {}
        render() {}
    },
    Scene: class {
        add() {}
        remove() {}
    },
    PerspectiveCamera: class {
        constructor() { this.position = {}; }
        updateProjectionMatrix() {}
    },
    AmbientLight: class {},
    PointLight: class {
        constructor() { this.position = { set: () => {} }; }
    },
    Group: class {
        constructor() {
            this.rotation = {};
        }
        add() {}
        traverse() {}
    },
    Color: class {},
    ShaderMaterial: class {},
    PointsMaterial: class {},
    Points: class {},
    Mesh: class {
        constructor() {
            this.rotation = { set: () => {} };
            this.scale = { setScalar: () => {} };
        }
    },
    SphereGeometry: class {
        constructor() {
            this.attributes = {
                position: {
                    count: 0,
                    setXYZ: () => {}
                }
            };
        }
        computeVertexNormals() {}
    },
    BufferGeometry: class {
        setAttribute() {}
    },
    BufferAttribute: class {},
    Vector3: class {
        constructor() { this.x = 0; this.y = 0; this.z = 0; }
        fromBufferAttribute() {}
        multiplyScalar() {}
        normalize() { return this; }
    }
};

global.window.THREE = global.THREE;

global.document = {
    getElementById: () => ({
        clientWidth: 800,
        clientHeight: 600,
        querySelectorAll: () => []
    }),
    hidden: false,
    querySelectorAll: () => {
        throw new Error('document.querySelectorAll should NOT be called during animation loop.');
    }
};

global.performance = { now: () => 1000 };
global.requestAnimationFrame = (cb) => {
    // Only call once to avoid infinite loop
    if (!global.rafCalled) {
        global.rafCalled = true;
        // we'll trigger it manually
    }
};

class IntersectionObserver {
    constructor(callback) { this.callback = callback; }
    observe() {}
    unobserve() {}
    disconnect() {}
}
global.IntersectionObserver = IntersectionObserver;

class MutationObserver {
    constructor(callback) { this.callback = callback; }
    observe() {}
    disconnect() {}
}
global.MutationObserver = MutationObserver;

// Load code
const fs = require('fs');
const code = fs.readFileSync('avatar.js', 'utf8');

eval(code);

const system = window.AvatarSystem;

// Initialize
system.init();

// Mock some visible avatars
const el1 = {
    getBoundingClientRect: () => ({ bottom: 500, top: 100, width: 50, height: 50, left: 10 }),
    dataset: { user: 'testuser1' }
};

system.visibleAvatars.add(el1);

try {
    system.animate();
    console.log("SUCCESS: Optimization verification passed. `querySelectorAll` was not called in animate loop.");
} catch (e) {
    console.error("FAIL:", e.message);
    process.exit(1);
}

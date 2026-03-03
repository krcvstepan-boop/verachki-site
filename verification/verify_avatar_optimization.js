// Mock browser environment for AvatarSystem
global.window = {
    innerHeight: 1000,
    devicePixelRatio: 1,
    addEventListener: () => {},
    THREE: {
        WebGLRenderer: class {
            constructor() {
                this.domElement = {};
            }
            setClearColor() {}
            setSize() {}
            setPixelRatio() {}
            setScissorTest() {}
            clear() {}
            setViewport() {}
            setScissor() {}
            render() {}
        },
        Scene: class { add() {} remove() {} },
        PerspectiveCamera: class { position = { z: 0 }; updateProjectionMatrix() {} },
        AmbientLight: class {},
        PointLight: class { position = { set: () => {} } },
        Group: class {
            constructor() { this.rotation = { x: 0, y: 0 }; }
            add() {}
            traverse() {}
        },
        Vector3: class {
            constructor(x=0, y=0, z=0) { this.x=x; this.y=y; this.z=z; }
            normalize() { return this; }
        },
        SphereGeometry: class {
            constructor() {
                this.attributes = {
                    position: {
                        count: 10,
                        setXYZ: () => {}
                    }
                };
            }
            computeVertexNormals() {}
        },
        BufferGeometry: class { setAttribute() {} },
        BufferAttribute: class {},
        Color: class {},
        ShaderMaterial: class {},
        PointsMaterial: class {},
        Mesh: class {
            constructor() {
                this.rotation = { set: () => {} };
                this.scale = { setScalar: () => {} };
            }
        },
        Points: class {},
        FrontSide: 0,
        AdditiveBlending: 0
    }
};

let querySelectorAllCount = 0;

global.document = {
    getElementById: (id) => {
        if (id === 'soul-avatars') {
            return { clientWidth: 800, clientHeight: 600, width: 800, height: 600 };
        }
        if (id === 'messages-container') {
            return {
                querySelectorAll: (selector) => {
                    if (selector === '.soul-avatar-placeholder') {
                        return []; // Mock initial pass
                    }
                    return [];
                }
            };
        }
        return null;
    },
    hidden: false,
    querySelectorAll: (selector) => {
        if (selector === '.soul-avatar-placeholder') {
            querySelectorAllCount++;
        }
        return [];
    }
};

global.performance = { now: () => Date.now() };

// Mock IntersectionObserver
global.IntersectionObserver = class {
    constructor(callback) {
        this.callback = callback;
    }
    observe() {}
    unobserve() {}
};

// Mock MutationObserver
global.MutationObserver = class {
    constructor() {}
    observe() {}
};

// Mock requestAnimationFrame to run exactly once synchronously for testing
global.requestAnimationFrame = (cb) => {
    // Prevent infinite loop by not actually scheduling
};

// Load the file
const fs = require('fs');
const code = fs.readFileSync('./avatar.js', 'utf8');
eval(code);

// Trigger a manual run of animate
window.AvatarSystem.animate();

console.log("querySelectorAll calls during animate:", querySelectorAllCount);
if (querySelectorAllCount === 0) {
    console.log("SUCCESS: document.querySelectorAll is not called in the animation loop.");
} else {
    console.error("FAILURE: document.querySelectorAll is still being called!");
    process.exit(1);
}

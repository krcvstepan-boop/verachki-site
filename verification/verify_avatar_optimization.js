const fs = require('fs');
const path = require('path');

// MOCKS
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
    AmbientLight: class { constructor() {} },
    PointLight: class { constructor() { this.position = { set: () => {} }; } },
    Group: class {
        constructor() { this.children = []; this.rotation = { x: 0, y: 0 }; }
        add(c) { this.children.push(c); }
        traverse(cb) { this.children.forEach(cb); }
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
        constructor() { this.x=0; this.y=0; this.z=0; }
        fromBufferAttribute() {}
        multiplyScalar() {}
        normalize() { return this; }
    },
    ShaderMaterial: class { constructor() { this.uniforms = { uTime: { value: 0 }}; } dispose() {} },
    Mesh: class { constructor() { this.rotation = { set: () => {} }; this.scale = { setScalar: () => {} }; this.isMesh = true; this.material = { uniforms: { uTime: { value: 0 }} }; } },
    BufferGeometry: class { constructor() { this.setAttribute = () => {}; } setAttribute() {} },
    BufferAttribute: class { constructor() {} },
    PointsMaterial: class { constructor() {} },
    Points: class { constructor() {} },
    Color: class { constructor() {} },
    FrontSide: 2
};

class DOMTokenList {
    constructor() { this._classes = new Set(); }
    add(c) { this._classes.add(c); }
    remove(c) { this._classes.delete(c); }
    contains(c) { return this._classes.has(c); }
}

class HTMLElement {
    constructor() {
        this.style = {};
        this.dataset = { user: 'test-user' };
        this.classList = new DOMTokenList();
        this.clientWidth = 100;
        this.clientHeight = 100;
        this.children = [];
        this.nodeType = 1; // ELEMENT_NODE
    }
    getBoundingClientRect() { return { top: 0, bottom: 100, left: 0, right: 100, width: 100, height: 100 }; }
    querySelector() { return null; }
    querySelectorAll() { return []; }
    addEventListener() {}
    appendChild(c) { this.children.push(c); }
}

global.HTMLElement = HTMLElement;

global.window = {
    addEventListener: () => {},
    innerWidth: 1000,
    innerHeight: 1000,
    devicePixelRatio: 1,
    THREE: global.THREE
};

let querySelectorCallCount = 0;
let observedElements = new Set();

global.document = {
    getElementById: (id) => new HTMLElement(), // Returns a generic element for 'messages-container'
    body: new HTMLElement(),
    querySelectorAll: (sel) => {
        if (sel === '.soul-avatar-placeholder') {
            querySelectorCallCount++;
        }
        return [];
    },
    createElement: () => new HTMLElement(),
    hidden: false
};

global.IntersectionObserver = class {
    constructor(cb) { this.cb = cb; }
    observe(el) { observedElements.add(el); } // Track calls
    unobserve(el) { observedElements.delete(el); }
    disconnect() {}
};

let mutationCallback = null;
global.MutationObserver = class {
    constructor(cb) {
        mutationCallback = cb; // Capture callback
        this.cb = cb;
    }
    observe() {}
    disconnect() {}
};

global.requestAnimationFrame = () => {};

// READ FILE
const code = fs.readFileSync(path.join(__dirname, '../avatar.js'), 'utf8');

// EXECUTE
// We use eval to load the class and instance into global scope
eval(code);

const system = window.AvatarSystem;

// TEST 1: Initial Scan & No Query in Loop
console.log("Running verification...");
system.init();
querySelectorCallCount = 0; // Reset
// Manually add mock
const mockAvatar = new HTMLElement();
mockAvatar.classList.add('soul-avatar-placeholder');
system.visibleAvatars.add(mockAvatar);

system.animate();

if (querySelectorCallCount > 0) {
    console.log(`FAIL 1: document.querySelectorAll('.soul-avatar-placeholder') was called ${querySelectorCallCount} times during animate loop.`);
    process.exit(1);
} else {
    console.log("PASS 1: document.querySelectorAll was NOT called in loop.");
}

// TEST 2: Mutation Observer Logic
if (!mutationCallback) {
    console.log("FAIL 2: MutationObserver was not initialized.");
    process.exit(1);
}

const newAvatar = new HTMLElement();
newAvatar.classList.add('soul-avatar-placeholder');

// Simulate mutation event
const mutationRecord = {
    addedNodes: [newAvatar],
    removedNodes: []
};
mutationCallback([mutationRecord]);

if (observedElements.has(newAvatar)) {
    console.log("PASS 2: New avatar was correctly observed by IntersectionObserver via MutationObserver.");
    process.exit(0);
} else {
    console.log("FAIL 2: New avatar was NOT observed.");
    process.exit(1);
}

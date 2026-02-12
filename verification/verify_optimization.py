from playwright.sync_api import sync_playwright
import os

def test_optimization():
    print("Starting optimization verification...")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Inject mock THREE.js
        page.add_init_script("""
            window.THREE = {
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
                PerspectiveCamera: class { constructor() { this.position = {z:0}; } updateProjectionMatrix() {} },
                AmbientLight: class { constructor() {} },
                PointLight: class { constructor() { this.position = {set:()=>{}}; } },
                Group: class { constructor() { this.rotation = {x:0, y:0}; this.children = []; } add(c) { this.children.push(c); } traverse() {} },
                SphereGeometry: class {
                    constructor() {
                        this.attributes = { position: { count: 10, setXYZ: () => {} }, fromBufferAttribute: () => {} };
                    }
                    computeVertexNormals() {}
                    dispose() {}
                },
                Vector3: class { constructor() { this.x=0; this.y=0; this.z=0; } fromBufferAttribute() {} multiplyScalar() {} normalize() { return this; } },
                ShaderMaterial: class { constructor() { this.uniforms = { uTime: { value: 0 }, uColor: { value: {} } }; } dispose() {} },
                Mesh: class { constructor() { this.rotation = {set:()=>{}}; this.scale = {set:()=>{}, setScalar:()=>{}}; this.isMesh = true; this.material = new window.THREE.ShaderMaterial(); } dispose() {} },
                BufferGeometry: class { setAttribute() {} },
                Float32Array: Float32Array,
                BufferAttribute: class {},
                PointsMaterial: class {},
                Points: class {},
                Color: class {},
                FrontSide: 0,
                AdditiveBlending: 1,
                Math: Math
            };
        """)

        # Load local file
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Wait for page load
        page.wait_for_load_state("domcontentloaded")

        # Mock showApp to make chat visible and init AvatarSystem
        page.evaluate("""
            () => {
                document.getElementById('app-interface').classList.remove('hidden');
                // Ensure AvatarSystem exists and force init
                if(window.AvatarSystem) {
                    console.log("Initializing AvatarSystem manually");
                    window.AvatarSystem.init();
                } else {
                    console.error("AvatarSystem not found");
                }
            }
        """)

        # Inject placeholders
        page.evaluate("""
            () => {
                const container = document.getElementById('messages-container');
                if (!container) return;

                // Clear existing
                container.innerHTML = '';

                // Add 10 placeholders
                for(let i=0; i<10; i++) {
                    const div = document.createElement('div');
                    div.className = 'soul-avatar-placeholder';
                    div.dataset.user = 'user' + i;
                    div.style.height = '50px';
                    div.style.width = '50px';
                    div.style.marginBottom = '10px';
                    div.style.background = 'red'; // Visibility
                    container.appendChild(div);
                }
                console.log("Injected 10 placeholders");
            }
        """)

        # Wait for JS to process (IntersectionObserver is async)
        page.wait_for_timeout(2000)

        # Check if visibleAvatars set exists and is populated
        result = page.evaluate("""
            () => {
                if (!window.AvatarSystem) return "AvatarSystem missing";
                if (!window.AvatarSystem.visibleAvatars) return "visibleAvatars property missing";
                return window.AvatarSystem.visibleAvatars.size;
            }
        """)

        print(f"Visible Avatars Count: {result}")

        # Also check if animate is running correctly (no errors)
        errors = []
        page.on("pageerror", lambda err: errors.append(err.message))

        if errors:
            print(f"Page errors: {errors}")

        browser.close()

if __name__ == "__main__":
    test_optimization()

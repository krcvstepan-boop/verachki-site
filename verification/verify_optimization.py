from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Capture console logs
        logs = []
        page.on("console", lambda msg: logs.append(msg.text))

        # Mock THREE.js
        page.evaluate("""
            window.THREE = {
                WebGLRenderer: class {
                    constructor() {
                        this.domElement = document.createElement('canvas');
                    }
                    setClearColor(c, a) {}
                    setSize(w, h, u) {}
                    setPixelRatio(r) {}
                    setScissorTest(t) {}
                    clear() {}
                    setViewport(x, y, w, h) {}
                    setScissor(x, y, w, h) {}
                    render(s, c) {}
                    dispose() {}
                },
                Scene: class {
                    constructor() { this.children = []; }
                    add(o) { this.children.push(o); }
                    remove(o) { const i = this.children.indexOf(o); if(i>-1) this.children.splice(i, 1); }
                },
                PerspectiveCamera: class {
                    constructor() { this.position = { z: 0, set: (x,y,z)=>{} }; }
                    updateProjectionMatrix() {}
                },
                AmbientLight: class { constructor() {} },
                PointLight: class { constructor() { this.position = { set: (x,y,z)=>{} }; } },
                Group: class {
                    constructor() { this.rotation = { x: 0, y: 0, set: ()=>{} }; this.scale = { setScalar: ()=>{} }; this.children=[]; }
                    add(o) { this.children.push(o); }
                    traverse(cb) { this.children.forEach(c => cb(c)); }
                },
                SphereGeometry: class {
                    constructor() {
                        this.attributes = {
                            position: { count: 10, array: new Float32Array(30), itemSize: 3, setXYZ: ()=>{} }
                        };
                    }
                    computeVertexNormals() {}
                    dispose() {}
                },
                BufferGeometry: class { setAttribute() {} dispose() {} },
                Vector3: class {
                    constructor(x,y,z) { this.x=x; this.y=y; this.z=z; }
                    fromBufferAttribute() { return this; }
                    multiplyScalar() {}
                    setXYZ() {}
                    normalize() { return this; }
                },
                ShaderMaterial: class { constructor() { this.uniforms={uTime:{value:0}}; } dispose() {} },
                PointsMaterial: class { constructor() {} dispose() {} },
                Mesh: class {
                    constructor() {
                        this.isMesh = true;
                        this.rotation = { set: () => {} };
                        this.scale = { setScalar: () => {} };
                        this.material = { uniforms: { uTime: { value: 0 } }, dispose: ()=>{} };
                        this.geometry = { dispose: ()=>{} };
                    }
                },
                Points: class { constructor() { this.geometry={dispose:()=>{}}; this.material={dispose:()=>{}}; } },
                Color: class { constructor() {} },
                BufferAttribute: class { constructor() {} },
                AdditiveBlending: 1,
                FrontSide: 1
            };
        """)

        # Setup DOM
        page.set_content("""
            <html>
            <body>
                <canvas id="soul-avatars" style="width: 800px; height: 600px;"></canvas>
                <div id="messages-container" style="height: 500px; overflow-y: scroll; position: relative;">
                    <!-- Messages will be injected here -->
                </div>
            </body>
            </html>
        """)

        # Inject avatar.js code
        with open('avatar.js', 'r') as f:
            script_content = f.read()
        page.add_script_tag(content=script_content)

        # 1. Verify Initialization
        print("Initializing AvatarSystem...")
        page.evaluate("window.AvatarSystem.init()")

        is_initialized = page.evaluate("window.AvatarSystem.initialized")
        if not is_initialized:
            print("❌ FAILURE: AvatarSystem.initialized is False after init()")
            exit(1)
        print("✅ AvatarSystem initialized.")

        # Check logs
        init_logs = [m for m in logs if "Soul ID System Initialized" in m]
        if len(init_logs) != 1:
            print(f"❌ FAILURE: Expected 1 init log, got {len(init_logs)}: {init_logs}")
            exit(1)

        # 2. Verify Idempotency
        print("Calling init() again...")
        page.evaluate("window.AvatarSystem.init()")

        init_logs_after = [m for m in logs if "Soul ID System Initialized" in m]
        if len(init_logs_after) != 1:
            print(f"❌ FAILURE: Init log appeared again! Idempotency failed. Logs: {init_logs_after}")
            exit(1)
        print("✅ Idempotency check passed (no extra init logs).")

        # 3. Verify visibleAvatars with MutationObserver
        print("Injecting messages...")
        page.evaluate("""
            const container = document.getElementById('messages-container');
            for(let i=0; i<10; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                row.style.height = '50px';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'User' + i;
                avatar.style.width = '40px';
                avatar.style.height = '40px';

                row.appendChild(avatar);
                container.appendChild(row);
            }
        """)

        # Wait for MutationObserver & IntersectionObserver
        page.wait_for_timeout(1000)

        visible_count = page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible Avatars: {visible_count}")

        if visible_count == 0:
            print("❌ FAILURE: No avatars detected as visible.")
            # Debug: Check if elements exist
            count = page.evaluate("document.querySelectorAll('.soul-avatar-placeholder').length")
            print(f"DOM Elements found: {count}")
            exit(1)

        print("✅ visibleAvatars populated successfully.")

        # 4. Verify removal updates visibleAvatars
        print("Removing messages...")
        page.evaluate("document.getElementById('messages-container').innerHTML = ''")
        page.wait_for_timeout(500)

        visible_count_after = page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible Avatars after clear: {visible_count_after}")

        if visible_count_after != 0:
             print("❌ FAILURE: visibleAvatars not cleared after DOM removal.")
             exit(1)

        print("✅ visibleAvatars cleared successfully.")
        print("Tests Passed!")

if __name__ == "__main__":
    run()

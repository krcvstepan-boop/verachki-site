
import os
import sys
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context(viewport={'width': 1280, 'height': 720})
        page = context.new_page()

        cwd = os.getcwd()
        index_path = os.path.join(cwd, 'index.html')
        url = f'file://{index_path}'

        # Block actual THREE.js from loading so our mock persists
        context.route("**/*three*", lambda route: route.abort())

        # Mock THREE with visual feedback (Canvas 2D fallback for visual verification)
        page.add_init_script("""
        window.THREE = {
            WebGLRenderer: class {
                constructor({canvas}) {
                    this.domElement = canvas || document.createElement('canvas');
                    // Mock WebGL by using 2D context to draw colored boxes for verification
                    this.context = this.domElement.getContext('2d');
                }
                setSize(w, h) {
                    this.domElement.width = w;
                    this.domElement.height = h;
                }
                setPixelRatio() {}
                setClearColor() {}
                setScissorTest() {}
                clear() {
                    if(this.context) this.context.clearRect(0,0,this.domElement.width, this.domElement.height);
                }
                setViewport() {}
                setScissor(x, y, w, h) {
                    this.scissor = {x, y, w, h};
                }
                render(scene, camera) {
                    if (this.context && this.scissor) {
                        this.context.fillStyle = 'rgba(0, 255, 0, 0.5)'; // Green indicates active render
                        const canvasHeight = this.domElement.height;
                        const yTop = canvasHeight - (this.scissor.y + this.scissor.h);
                        this.context.fillRect(this.scissor.x, yTop, this.scissor.w, this.scissor.h);
                    }
                }
                dispose() {}
            },
            Scene: class {
                constructor() { this.children = []; }
                add(obj) { this.children.push(obj); }
                remove(obj) { const idx = this.children.indexOf(obj); if (idx > -1) this.children.splice(idx, 1); }
            },
            PerspectiveCamera: class { constructor() { this.position = { z: 0 }; } updateProjectionMatrix() {} },
            AmbientLight: class {},
            PointLight: class { constructor() { this.position = { set: () => {} }; } },
            Group: class { constructor() { this.children = []; this.rotation = { x: 0, y: 0 }; this.scale = { setScalar: () => {} }; } add(obj) { this.children.push(obj); } traverse() {} },
            SphereGeometry: class { constructor() { this.attributes = { position: { count: 0, fromBufferAttribute: () => {}, setXYZ: () => {} } }; } computeVertexNormals() {} dispose() {} },
            Vector3: class { constructor() { this.x=0; this.y=0; this.z=0; } fromBufferAttribute() {} multiplyScalar() {} normalize() { return this; } },
            ShaderMaterial: class { constructor() { this.uniforms = { uTime: { value: 0 } }; } dispose() {} },
            Mesh: class { constructor() { this.rotation = { set: () => {} }; this.scale = { setScalar: () => {} }; this.isMesh = true; this.material = { uniforms: { uTime: { value: 0 } } }; } },
            Color: class {},
            BufferGeometry: class { setAttribute() {} },
            BufferAttribute: class {},
            PointsMaterial: class {},
            Points: class {},
            FrontSide: 0,
            AdditiveBlending: 0
        };
        """)

        print(f"Loading {url}...")
        page.goto(url)

        # Show App Interface
        page.evaluate("document.getElementById('app-interface').classList.remove('hidden')")
        page.evaluate("document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'))")

        # Initialize AvatarSystem
        page.wait_for_function("() => window.AvatarSystem !== undefined")
        page.evaluate("window.AvatarSystem.init()")

        # Add dummy messages to visualize avatars
        print("Injecting messages...")
        page.evaluate("""
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            for(let i=0; i<5; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                row.style.marginBottom = '20px';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'User' + i;
                avatar.style.width = '60px';
                avatar.style.height = '60px';
                avatar.style.border = '1px dashed red'; // Border to show where it should be

                const msg = document.createElement('div');
                msg.className = 'message';
                msg.innerText = 'Test Message ' + i;

                row.appendChild(avatar);
                row.appendChild(msg);
                container.appendChild(row);
            }
        """)

        # Wait for render loop to draw green boxes
        page.wait_for_timeout(1000)

        screenshot_path = os.path.join(cwd, 'verification/visual_verification.png')
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()

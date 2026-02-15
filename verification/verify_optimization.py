
import os
import sys
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        # Get absolute path to index.html
        cwd = os.getcwd()
        index_path = os.path.join(cwd, 'index.html')
        # On Windows it might need file:///, but let's assume Linux/Mac in sandbox
        url = f'file://{index_path}'

        # Mock THREE.js to avoid network dependency and ensure init runs
        page.add_init_script("""
        window.THREE = {
            WebGLRenderer: class {
                constructor() { this.domElement = document.createElement('canvas'); }
                setSize() {}
                setPixelRatio() {}
                setClearColor() {}
                setScissorTest() {}
                clear() {}
                setViewport() {}
                setScissor() {}
                render() {}
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

        # Ensure AvatarSystem is available
        try:
            page.wait_for_function("() => window.AvatarSystem !== undefined", timeout=5000)
        except:
            print("AvatarSystem not found or timed out.")
            sys.exit(1)

        # Initialize AvatarSystem manually (normally showApp does it)
        # We need to make sure the canvas exists. It does in index.html.
        print("Initializing AvatarSystem...")
        # Mock container if it doesn't exist (it should)
        if not page.evaluate("!!document.getElementById('messages-container')"):
             print("Error: messages-container not found")
             sys.exit(1)

        page.evaluate("window.AvatarSystem.init()")

        # Check if visibleAvatars Set exists (it won't until we apply the patch)
        has_optimization = page.evaluate("!!window.AvatarSystem.visibleAvatars")

        if not has_optimization:
            print("Optimization NOT detected (visibleAvatars Set missing).")
            # If we run this before patching, just exit gracefully
            browser.close()
            return

        print("Optimization DETECTED.")

        # Create a test environment
        # Make sure app interface is visible
        page.evaluate("document.getElementById('app-interface').classList.remove('hidden')")

        # Clear existing messages
        page.evaluate("document.getElementById('messages-container').innerHTML = ''")

        # Inject CSS to make sure container is visible and has size
        page.add_style_tag(content="""
            #app-interface {
                display: block !important;
            }
            #messages-container {
                display: block !important;
                height: 500px !important;
                width: 500px !important;
                overflow: auto !important;
                background: white;
            }
            .message-row {
                height: 60px;
                display: flex;
            }
            .soul-avatar-placeholder {
                width: 50px;
                height: 50px;
                background: red;
                display: block !important;
            }
        """)

        # Add a test message with avatar placeholder
        print("Adding test message...")
        page.evaluate("""
            const container = document.getElementById('messages-container');
            const row = document.createElement('div');
            row.className = 'message-row';
            const avatar = document.createElement('div');
            avatar.className = 'soul-avatar-placeholder';
            avatar.dataset.user = 'TestUser';
            row.appendChild(avatar);
            container.appendChild(row);
        """)

        # Wait a bit for MutationObserver and IntersectionObserver
        page.wait_for_timeout(1000) # Increased timeout to be safe

        # Check if avatar is in visibleAvatars
        size = page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible Avatars: {size}")

        # Force a scroll/layout recalc just in case headless needs it
        page.evaluate("window.scrollTo(0, 0); document.body.offsetHeight;")

        if size < 1:
            print(f"FAIL: Expected >= 1 visible avatar, got {size}")
            # Debug info
            rect = page.evaluate("""
                const el = document.querySelector('.soul-avatar-placeholder');
                const r = el.getBoundingClientRect();
                JSON.stringify({
                    top: r.top, bottom: r.bottom,
                    height: r.height, width: r.width,
                    windowHeight: window.innerHeight
                })
            """)
            print(f"Element Rect: {rect}")
            sys.exit(1)
        else:
            print("PASS: Avatar detected as visible.")

            # Test removing
            print("Removing test message...")
            page.evaluate("document.querySelector('.message-row').remove()")
            page.wait_for_timeout(500)
            size = page.evaluate("window.AvatarSystem.visibleAvatars.size")
            print(f"Visible Avatars after remove: {size}")
            if size != 0:
                print(f"FAIL: Expected 0 visible avatars, got {size}")
                sys.exit(1)
            else:
                print("PASS: Avatar removed from set.")

        browser.close()

if __name__ == "__main__":
    run()

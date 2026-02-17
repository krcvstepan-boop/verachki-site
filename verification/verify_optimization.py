from playwright.sync_api import sync_playwright
import os
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a context with permissions if needed, though standard should be fine
        context = browser.new_context()
        page = context.new_page()

        # Path to index.html
        file_path = os.path.abspath("index.html")
        url = f"file://{file_path}"

        print(f"Loading {url}...")

        # Inject mock BEFORE loading to ensure it captures early script execution
        page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                    subscribe() { return { unsubscribe: () => {} }; }
                },
                Account: class {
                    get() { return Promise.reject("Mock Error"); }
                    createEmailPasswordSession() { return Promise.resolve({}); }
                    deleteSession() { return Promise.resolve({}); }
                },
                Databases: class {
                    listDocuments() { return Promise.resolve({documents: []}); }
                    createDocument() { return Promise.resolve({}); }
                    updateDocument() { return Promise.resolve({}); }
                    deleteDocument() { return Promise.resolve({}); }
                },
                Storage: class {
                    getFileView() { return ""; }
                    createFile() { return Promise.resolve({$id: 'file'}); }
                },
                ID: { unique: () => 'unique_id' },
                Query: {
                    equal: () => '',
                    orderAsc: () => '',
                    limit: () => ''
                }
            };
        """)

        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Manually initialize AvatarSystem and add messages
        print("Initializing AvatarSystem and adding messages...")
        page.evaluate("""
            // Ensure container exists and is visible (mocking showApp)
            const app = document.getElementById('app-interface');
            app.classList.remove('hidden');

            const container = document.getElementById('messages-container');
            container.innerHTML = '';

            // Force Init
            if (window.AvatarSystem) {
                // Mock THREE.WebGLRenderer to avoid WebGL context errors in headless if any
                if (!window.THREE) window.THREE = {};
                if (!window.THREE.WebGLRenderer) {
                     window.THREE.WebGLRenderer = class {
                         constructor() { this.domElement = document.createElement('canvas'); }
                         setSize() {}
                         setPixelRatio() {}
                         setClearColor() {}
                         render() {}
                         setScissorTest() {}
                         clear() {}
                         setViewport() {}
                         setScissor() {}
                         dispose() {}
                     };
                     window.THREE.Scene = class { add() {} remove() {} };
                     window.THREE.PerspectiveCamera = class { updateProjectionMatrix() {} };
                     window.THREE.AmbientLight = class {};
                     window.THREE.PointLight = class { position = { set: () => {} }; };
                     window.THREE.Group = class { add() {} rotation = {x:0, y:0}; traverse() {} };
                     window.THREE.SphereGeometry = class { attributes = { position: { count: 10, fromBufferAttribute: () => {}, setXYZ: () => {} } }; computeVertexNormals() {} dispose() {} };
                     window.THREE.ShaderMaterial = class { dispose() {} };
                     window.THREE.Mesh = class { rotation = { set: () => {} }; scale = { setScalar: () => {} }; };
                     window.THREE.Vector3 = class { fromBufferAttribute() {} multiplyScalar() {} normalize() {} };
                     window.THREE.Color = class {};
                     window.THREE.BufferGeometry = class { setAttribute() {} };
                     window.THREE.BufferAttribute = class {};
                     window.THREE.PointsMaterial = class {};
                     window.THREE.Points = class {};
                }

                window.AvatarSystem.init();
            }
        """)

        # Add messages
        page.evaluate("""
            const container = document.getElementById('messages-container');
            for(let i=0; i<50; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                // Make each message tall enough so scrolling matters
                row.style.height = '100px';
                row.style.marginBottom = '20px';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'user' + i;
                avatar.style.width = '50px';
                avatar.style.height = '50px';
                avatar.style.display = 'block';

                row.appendChild(avatar);
                container.appendChild(row);
            }
        """)

        # Wait for IntersectionObserver
        page.wait_for_timeout(2000)

        # Verify visible count
        visible_count = page.evaluate("window.AvatarSystem.visibleAvatars ? window.AvatarSystem.visibleAvatars.size : -1")
        print(f"Visible Avatars: {visible_count}")

        if visible_count == -1:
            print("FAILURE: visibleAvatars Set not found on AvatarSystem.")
            sys.exit(1)

        if visible_count == 0:
            print("FAILURE: No avatars detected visible (expected some).")
            sys.exit(1)

        if visible_count >= 50:
             print(f"FAILURE: All avatars visible ({visible_count}). Culling not working or viewport too big.")
             sys.exit(1)

        print("SUCCESS: Optimization logic verified.")
        browser.close()

if __name__ == "__main__":
    run()


import os
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Block external scripts to ensure mocks are used
        page.route("**/*three.min.js", lambda route: route.abort())
        page.route("**/*appwrite*", lambda route: route.abort())

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        # Mock THREE.js and Appwrite to avoid network dependency and errors
        page.add_init_script("""
            window.THREE = {
                WebGLRenderer: class {
                    constructor() { this.domElement = document.createElement('canvas'); }
                    setSize(){} setPixelRatio(){} setClearColor(){} render(){} setScissorTest(){} clear(){} setScissor(){} setViewport(){}
                },
                Scene: class { add(){} remove(){} },
                PerspectiveCamera: class { position={z:0}; updateProjectionMatrix(){} },
                AmbientLight: class {},
                PointLight: class { position={set(){}} },
                Group: class { add(){} remove(){} traverse(){} rotation={x:0,y:0} },
                SphereGeometry: class { attributes={position:{count:0, setXYZ:()=>{}}, normal:{count:0}}; computeVertexNormals(){} },
                ShaderMaterial: class { dispose(){} },
                Mesh: class { rotation={set(){}}; scale={setScalar(){}}; material={uniforms:{uTime:{value:0}}}; geometry={dispose:()=>{}} },
                Vector3: class { fromBufferAttribute(){} multiplyScalar(){} normalize(){} set(){} },
                Color: class {},
                BufferGeometry: class { setAttribute(){} dispose(){} },
                BufferAttribute: class {},
                PointsMaterial: class { dispose(){} },
                Points: class { geometry={dispose:()=>{}}; material={dispose:()=>{}} },
                MathUtils: { randFloat: () => 0 },
                FrontSide: 0,
                AdditiveBlending: 0
            };

            window.Appwrite = {
                Client: class { setEndpoint(){ return this; } setProject(){ return this; } subscribe(){ return { unsubscribe: ()=>{} }; } },
                Account: class { get(){ return new Promise(()=>{}); } },
                Databases: class { listDocuments(){ return new Promise(()=>{}); } },
                Storage: class {},
                ID: { unique: () => 'unique' },
                Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
            };
        """)

        # Load local index.html
        page.goto(f"file://{os.getcwd()}/index.html")

        # Inject logic to verify AvatarSystem
        # We need to manually init AvatarSystem because we mocked Appwrite/Auth
        page.evaluate("""
            // Show App Interface so IO works
            document.getElementById('app-interface').classList.remove('hidden');

            // Force Init
            window.AvatarSystem.container = document.getElementById('messages-container');
            window.AvatarSystem.init();
        """)

        print("Initialized AvatarSystem.")

        # Inject placeholders
        page.evaluate("""
            const container = document.getElementById('messages-container');
            container.style.height = '500px';
            container.style.overflow = 'auto';
            container.style.display = 'block';

            // Create 20 items, each 100px high
            for(let i=0; i<20; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                row.style.height = '100px';
                row.style.marginBottom = '10px';

                const p = document.createElement('div');
                p.className = 'soul-avatar-placeholder';
                p.dataset.user = 'user'+i;
                p.style.width = '50px';
                p.style.height = '50px';
                p.style.background = 'red'; // Visible for debug

                row.appendChild(p);
                container.appendChild(row);
            }
        """)

        print("Injected 20 avatars.")

        # Check if visibleAvatars set exists (after optimization it should)
        # For now, we expect it NOT to exist or be empty if not implemented.
        # But we are verifying the optimization, so this script is for AFTER changes too?
        # The prompt says "Create a reproduction/verification script... Once you have finished this... move on".
        # So this script should fail or show "not implemented" now, and pass later.

        # We'll check if the property exists
        has_optimization = page.evaluate("!!window.AvatarSystem.visibleAvatars")
        print(f"Has visibleAvatars property: {has_optimization}")

        has_io = page.evaluate("!!window.AvatarSystem.io")
        print(f"Has IntersectionObserver: {has_io}")

        has_mo = page.evaluate("!!window.AvatarSystem.mo")
        print(f"Has MutationObserver: {has_mo}")

        # Trigger scroll
        page.evaluate("document.getElementById('messages-container').scrollTop = 1000;")
        page.wait_for_timeout(1000) # Wait for IntersectionObserver

        if has_optimization:
            count = page.evaluate("window.AvatarSystem.visibleAvatars.size")
            print(f"Visible Avatars Count: {count}")
            # With 500px height and 110px items, roughly 5 items should be visible
            if count > 0 and count < 20:
                print("SUCCESS: Optimization working (subset visible).")
            else:
                # Debug visible set content
                debug_info = page.evaluate("""
                    Array.from(window.AvatarSystem.visibleAvatars).map(el => el.dataset.user)
                """)
                print(f"Visible users: {debug_info}")
                print("FAILURE: Count suspicious.")
        else:
            print("Optimization not yet implemented.")

        browser.close()

if __name__ == "__main__":
    run()

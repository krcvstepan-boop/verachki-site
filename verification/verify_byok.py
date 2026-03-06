from playwright.sync_api import sync_playwright

def test_byok_prompt():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a new context so we have a clean localStorage
        context = browser.new_context()
        page = context.new_page()

        # Mock Appwrite to prevent defer script loading issues
        context.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } },
                Account: class { get() { return Promise.reject(); } },
                Databases: class {},
                Storage: class {},
                ID: { unique: () => '123' },
                Query: class {}
            };
            window.THREE = {
                WebGLRenderer: class { setSize() {} setPixelRatio() {} setClearColor() {} setScissorTest() {} clear() {} setViewport() {} setScissor() {} render() {} },
                Scene: class { add() {} remove() {} },
                PerspectiveCamera: class { position = { z: 0 } },
                AmbientLight: class {},
                PointLight: class { position = { set: () => {} } },
                Group: class { add() {} traverse() {} rotation = {x:0, y:0} },
                SphereGeometry: class { attributes = { position: { count: 0 } } computeVertexNormals() {} },
                Vector3: class { fromBufferAttribute() {} multiplyScalar() {} normalize() { return this; } set() {} },
                Color: class {},
                ShaderMaterial: class {},
                Mesh: class { rotation = { set: () => {} }; scale = { setScalar: () => {} } },
                BufferGeometry: class { setAttribute() {} },
                Float32Array: Float32Array,
                BufferAttribute: class {},
                PointsMaterial: class {},
                Points: class {},
                AdditiveBlending: 1,
                FrontSide: 1
            };

            // Mock prompt to automatically return a dummy token
            window.promptCount = 0;
            window.prompt = function(message) {
                window.promptCount++;
                return "dummy_token_123";
            };
        """)

        # Navigate to the local server
        page.goto("http://127.0.0.1:8080/index.html", wait_until='domcontentloaded')

        # To test askMistral, we can execute it in the page context
        result = page.evaluate("""async () => {
            // First time it should prompt because localStorage is empty
            const res1 = await window.askMistral('test', true);

            // Now let's check localStorage
            const token = localStorage.getItem('HF_TOKEN');

            return {
                promptCount: window.promptCount,
                token: token
            };
        }""")

        print(f"Result: {result}")

        # Take a screenshot to show the app is running
        page.screenshot(path="verification/verification.png")

        browser.close()

if __name__ == "__main__":
    test_byok_prompt()

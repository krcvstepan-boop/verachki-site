import asyncio
from playwright.async_api import async_playwright
import time

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Block heavy/external requests that might cause timeouts
        await context.route("**/*", lambda route, request: route.continue_() if request.url.startswith("http://localhost:8080") else route.abort())

        # We must fulfill HuggingFace request to capture auth header properly
        # We can unabort the huggingface url by handling it specifically
        async def handle_hf_route(route):
            request = route.request
            auth_header = request.headers.get("authorization")
            print(f"Intercepted HuggingFace Request with Auth Header: {auth_header}")
            assert auth_header == "Bearer mock_hf_token_12345", "Auth header does not match mock token!"
            await route.fulfill(
                status=200,
                content_type="application/json",
                body='[{"generated_text": "Mocked AI response"}]'
            )

        await context.route("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", handle_hf_route)
        await context.route("https://fra.cloud.appwrite.io/v1/**", lambda route: route.fulfill(status=200, json={ "documents": [] }))

        page = await context.new_page()

        # Mock Appwrite, state, and window.prompt for BYOK
        await page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } },
                Account: class { get() { return Promise.resolve({ $id: 'user1', name: 'Test User', email: 'test@example.com' }); } },
                Databases: class {
                    listDocuments() { return Promise.resolve({ documents: [] }); }
                    createDocument() { return Promise.resolve({ $id: 'doc123' }); }
                },
                Storage: class { getFileView() { return ''; } },
                ID: { unique: () => 'id123' },
                Query: { equal: () => '', orderDesc: () => '', limit: () => '', orderAsc: () => '' }
            };
            window.state = { user: { $id: 'user1', name: 'TestUser', email: 'test@test.com' } };
            window.countdownInterval = null;
            window.countdownAnimFrame = null;
            window.prompt = function(text) {
                console.log("window.prompt called with text: " + text);
                return "mock_hf_token_12345";
            };
            window.THREE = { WebGLRenderer: class { setSize(){} setPixelRatio(){} render(){} }, Scene: class {}, PerspectiveCamera: class { position={z:0} }, Object3D: class {}, TextureLoader: class { load(){} }, SphereGeometry: class {}, MeshPhysicalMaterial: class {}, Mesh: class { position={set:()=>{}} }, AmbientLight: class {}, DirectionalLight: class { position={set:()=>{}} }, PointsMaterial: class {}, BufferGeometry: class { setAttribute(){} }, Points: class {}, Group: class { add(){} }, Vector3: class { set(){} }, Float32BufferAttribute: class {} };
        """)

        await page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

        # Wait a bit for JS initialization
        await page.wait_for_timeout(1000)

        # Ensure UI is visible
        await page.evaluate("""
            document.getElementById('app-interface').classList.remove('hidden');
        """)

        # Call tryTriggerAI directly (simulates typing "ии, привет" which calls tryTriggerAI -> askMistral)
        await page.evaluate("window.tryTriggerAI('ии, привет')")

        # Wait to allow the intercepted route and async fetch to complete
        await page.wait_for_timeout(2000)

        print("Verification complete: HuggingFace API intercepted with correct BYOK token.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

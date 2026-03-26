import os
from playwright.sync_api import sync_playwright

def verify_byok_ai_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Record video
        context = browser.new_context(record_video_dir="verification/video")
        page = context.new_page()

        # Mock Appwrite Client and Realtime connection to avoid hanging and simplify test
        page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                    subscribe() { return this; }
                },
                Account: class {
                    get() { return Promise.resolve({ $id: 'test-user', name: 'Tester', email: 'test@example.com' }); }
                },
                Databases: class {
                    listDocuments() { return Promise.resolve({ documents: [{
                        $id: 'doc1', username: 'Tester', rank: 'User', ether: 0, flower_xp: 0
                    }]}); }
                    createDocument() { return Promise.resolve({ $id: 'new-doc' }); }
                },
                Storage: class {},
                ID: { unique: () => 'id-' + Math.random() },
                Query: { equal: () => '', orderAsc: () => '', limit: () => '' }
            };

            // Mock window.prompt to simulate user entering HF token
            window.prompt = function(message) {
                console.log("MOCKED PROMPT CALLED with message:", message);
                return "mock_hf_token_123";
            };

            // Setup state
            window.state = {
                user: { $id: 'test-user', name: 'Tester', email: 'test@example.com' },
                profile: { $id: 'doc1', username: 'Tester', rank: 'User', ether: 0, flower_xp: 0 },
                profileCache: new Map(),
                aiCooldown: false
            };
        """)

        # Block appwrite requests just in case
        page.route("**/v1/account", lambda route: route.fulfill(status=200, json={"$id": "test", "name": "Test", "email": "test@test.com"}))
        page.route("**/v1/databases/*/collections/*/documents*", lambda route: route.fulfill(status=200, json={"documents": []}))
        page.route("**/v1/realtime*", lambda route: route.abort())

        # Mock Hugging Face API
        def handle_hf_route(route):
            request = route.request
            auth_header = request.headers.get("authorization")
            print(f"HF Request Auth Header: {auth_header}")

            if auth_header == "Bearer mock_hf_token_123":
                route.fulfill(status=200, json=[{"generated_text": "Mocked AI Response from Verachka!"}])
            else:
                route.fulfill(status=401, json={"error": "Unauthorized"})

        page.route("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", handle_hf_route)

        try:
            # Go to local app
            page.goto("http://localhost:8080")

            # Bypass landing screen directly
            page.evaluate("""
                document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
                document.getElementById('app-interface').classList.remove('hidden');

                // Clear any existing token to force prompt
                localStorage.removeItem('HF_TOKEN');
            """)

            # Trigger AI directly
            print("Triggering AI via direct call...")
            page.evaluate("window.tryTriggerAI('система, привет!')")

            # Wait a moment for promises to resolve
            page.wait_for_timeout(2000)

            # Check if token was saved
            token_in_storage = page.evaluate("localStorage.getItem('HF_TOKEN')")
            print(f"Token in localStorage: {token_in_storage}")

            # Take screenshot
            page.screenshot(path="verification/verification.png")
            print("Screenshot saved to verification/verification.png")

        except Exception as e:
            print(f"Error during verification: {e}")
            page.screenshot(path="verification/error.png")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    verify_byok_ai_flow()
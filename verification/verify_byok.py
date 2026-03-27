import json
from playwright.sync_api import sync_playwright

def run_cuj(page):
    # Mock window.prompt to return our test token
    page.add_init_script("""
        window.prompt = function(message) {
            console.log('Prompt triggered:', message);
            return 'test_mock_token_123';
        };
        // Mock Appwrite global state so UI renders correctly
        window.state = {
            user: { $id: 'user1', name: 'TestUser', email: 'test@test.com' },
            profile: { $id: 'prof1', username: 'TestUser', rank: 'Наблюдатель' },
            profileCache: new Map(),
            isLogin: true,
            aiCooldown: false
        };
    """)

    # Mock huggingface API to prevent real network calls and test BYOK auth headers
    def handle_hf_route(route):
        headers = route.request.headers
        auth_header = headers.get('authorization', '')
        print("HF Request Auth Header:", auth_header)

        # Verify the token we injected via prompt is being used
        if 'test_mock_token_123' in auth_header:
            route.fulfill(
                status=200,
                json=[{"generated_text": "Mocked AI Response using BYOK"}],
                headers={'Access-Control-Allow-Origin': '*'}
            )
        else:
            route.fulfill(status=401, json={"error": "Unauthorized"})

    page.route("https://api-inference.huggingface.co/models/mistralai/*", handle_hf_route)

    # Mock Appwrite endpoints
    page.route("**/v1/databases/*/collections/*/documents*", lambda route: route.fulfill(status=200, json={"documents": []}))
    page.route("**/v1/account", lambda route: route.fulfill(status=200, json={"$id": "user1", "name": "TestUser", "email": "test@test.com"}))
    page.route("**/v1/realtime*", lambda route: route.abort()) # Abort realtime to prevent hangs

    page.goto("http://localhost:8080")
    page.wait_for_timeout(1000)

    # Bypass auth and show main app interface
    page.evaluate("""
        document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
        document.getElementById('app-interface').classList.remove('hidden');
        window.scrollTo(0, 0);
    """)
    page.wait_for_timeout(500)

    # 1. Clear local storage to ensure prompt is triggered
    page.evaluate("localStorage.removeItem('HF_TOKEN');")

    # 2. Trigger interactive AI call
    print("Triggering interactive AI call...")
    page.evaluate("window.tryTriggerAI('система, привет');")
    page.wait_for_timeout(1000)

    # 3. Verify token was saved to localStorage
    saved_token = page.evaluate("localStorage.getItem('HF_TOKEN');")
    print("Saved Token in localStorage:", saved_token)
    assert saved_token == 'test_mock_token_123'

    # 4. Trigger non-interactive AI call to ensure it uses saved token without prompt
    print("Triggering non-interactive AI call (should use saved token)...")
    page.evaluate("window.tryTriggerAI('система, как дела');")
    page.wait_for_timeout(1000)

    page.screenshot(path="verification/screenshots/verify_byok.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    import os
    os.makedirs("verification/videos", exist_ok=True)
    os.makedirs("verification/screenshots", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(record_video_dir="verification/videos")
        page = context.new_page()

        # Listen for console logs to verify prompt was called
        page.on("console", lambda msg: print(f"Browser Console: {msg.text}"))

        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()

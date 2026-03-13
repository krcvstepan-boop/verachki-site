from playwright.sync_api import sync_playwright
import time

def test_byok_flow(page):
    # Route for huggingface to simulate API call
    page.route("https://api-inference.huggingface.co/**/*", lambda route: route.fulfill(
        status=200,
        json=[{"generated_text": "Mocked AI response"}]
    ))

    # Mock Appwrite to bypass login
    page.add_init_script("""
        window.Appwrite = {
            Client: class { setEndpoint() { return this; } setProject() { return this; } },
            Account: class { get() { return Promise.resolve({ $id: 'user123', name: 'Test User', email: 'test@example.com' }); } },
            Databases: class {
                listDocuments() { return Promise.resolve({ documents: [{ $id: 'prof1', username: 'Test User', email: 'test@example.com', rank: 'Наблюдатель', flower_xp: 10, ether: 5 }] }); }
                createDocument() { return Promise.resolve({}); }
            },
            Storage: class { getFileView() { return ''; } },
            ID: { unique: () => 'id' + Date.now() },
            Query: { equal: () => '', orderAsc: () => '', limit: () => '' }
        };
        window.state = { user: null, profile: null, profileCache: new Map() };
    """)

    # Mock window.prompt to provide our token
    page.add_init_script("""
        window.prompt = function(msg) {
            console.log("Prompt called with: " + msg);
            return "mock_hf_token_from_prompt";
        };
    """)

    page.goto("http://localhost:8080/index.html")

    # Wait for the app to load and show App
    page.evaluate("showApp()")
    page.wait_for_selector("#app-interface:not(.hidden)", state="visible", timeout=10000)

    # Trigger tryTriggerAI which should call askMistral, which should trigger our mocked window.prompt
    # and save the token to localStorage.

    # We clear localStorage first to ensure the prompt is triggered
    page.evaluate("localStorage.removeItem('HF_TOKEN')")

    # Call tryTriggerAI with a direct call phrase
    page.evaluate("tryTriggerAI('Система, привет')")

    # Wait a moment for the async operations to complete
    time.sleep(2)

    # Check localStorage for the token
    token = page.evaluate("localStorage.getItem('HF_TOKEN')")
    print(f"Token in localStorage: {token}")
    assert token == "mock_hf_token_from_prompt", "Token was not saved to localStorage!"

    # Take a screenshot of the chat interface
    page.screenshot(path="verification/sentinel_byok_test.png")
    print("Verification complete.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            test_byok_flow(page)
        finally:
            browser.close()

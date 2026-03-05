from playwright.sync_api import Page, expect, sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block external resources for stability
        context = browser.new_context()
        context.route("**/*", lambda route: route.continue_() if route.request.resource_type in ["document", "script", "xhr", "fetch"] else route.abort())

        page = context.new_page()

        # Disable waiting for fonts on screenshot
        page.add_init_script("""
            window.prompt = function(msg) {
                console.log("Prompt called with:", msg);
                return "mock_hf_token_123";
            };
        """)

        # Mock Appwrite to prevent network errors blocking execution
        page.add_init_script("""
            window.Appwrite = {
                Client: function() { return { setEndpoint: () => this, setProject: () => this }; },
                Account: function() { return { get: async () => ({ $id: 'test', name: 'Tester' }) }; },
                Databases: function() { return {
                    listDocuments: async () => ({ documents: [] }),
                    createDocument: async () => ({})
                }; },
                Storage: function() { return {}; },
                ID: { unique: () => 'id123' },
                Query: { orderDesc: () => {}, limit: () => {}, equal: () => {}, orderAsc: () => {} }
            };
        """)

        # Override fetch to intercept Mistral API calls
        page.add_init_script("""
            const originalFetch = window.fetch;
            window.fetch = async function() {
                if (arguments[0].includes('mistralai')) {
                    console.log("Mistral API called with headers:", arguments[1].headers);
                    return {
                        ok: true,
                        json: async () => [{ generated_text: "Mocked AI Response" }]
                    };
                }
                return originalFetch.apply(this, arguments);
            };
        """)

        print("Navigating to index.html...")
        page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

        # Wait for script to initialize state
        page.wait_for_timeout(1000)

        # Force state to logged in to bypass auth screen and show chat
        page.evaluate("""
            window.state.user = { $id: 'test', name: 'Tester' };
            window.showApp();
            document.fonts.ready.then(() => { window.__fonts_ready = true; });
        """)
        page.wait_for_timeout(500)

        # Trigger AI
        print("Triggering AI...")
        page.evaluate("window.tryTriggerAI('ИИ, привет!')")
        page.wait_for_timeout(1000)

        # Check localStorage to see if token was saved
        token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        print(f"Token in localStorage: {token}")

        if token == "mock_hf_token_123":
            print("SUCCESS: Token was successfully retrieved via prompt and saved to localStorage.")
        else:
            print("ERROR: Token was not saved correctly.")

        browser.close()

if __name__ == "__main__":
    run()

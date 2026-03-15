from playwright.sync_api import sync_playwright, Page, expect

def test_byok(page: Page):
    # Mock Appwrite to bypass login
    page.add_init_script("""
        window.Appwrite = {
            Client: class { setEndpoint() { return this; } setProject() { return this; } },
            Account: class { async get() { return { $id: 'u1', email: 'test@test.com', name: 'tester' }; } },
            Databases: class {
                async listDocuments() { return { documents: [] }; }
                async createDocument() { return { $id: 'doc1' }; }
            },
            Storage: class {},
            ID: { unique: () => 'id' },
            Query: { equal: () => '', orderAsc: () => '', limit: () => '' }
        };
        window.state = {
            user: { $id: 'u1', email: 'test@test.com', name: 'tester' },
            profile: { $id: 'p1', username: 'tester', rank: 'User', ether: 0, flower_xp: 0 },
            profileCache: new Map(),
            isLogin: true,
            aiCooldown: false
        };
        window.countdownInterval = null;
        window.countdownAnimFrame = null;
    """)

    # Navigate to app
    page.goto("http://localhost:8080/index.html")

    # Inject script to mock prompt and fetch
    page.evaluate("""
        window.promptCalls = 0;
        window.originalPrompt = window.prompt;
        window.prompt = function(msg) {
            window.promptCalls++;
            return 'my-test-token-123';
        };

        window.originalFetch = window.fetch;
        window.fetch = async function(url, options) {
            if (url && url.includes && url.includes('huggingface.co')) {
                window.lastFetchHeaders = options.headers;
                return {
                    ok: true,
                    status: 200,
                    json: async () => [{ generated_text: "Mock AI reply" }]
                };
            }
            return window.originalFetch(url, options);
        };
    """)

    # Clear token to test prompt
    page.evaluate("localStorage.removeItem('HF_TOKEN')")

    # Trigger AI interactively (should prompt and set token)
    page.evaluate("askMistral('test interactive', true)")

    # Allow async operations to complete
    page.wait_for_timeout(500)

    # Check that prompt was called
    prompt_calls = page.evaluate("window.promptCalls")
    assert prompt_calls == 1, "Prompt was not called for missing token in interactive mode."

    # Check token in localStorage
    saved_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
    assert saved_token == 'my-test-token-123', "Token was not saved to localStorage."

    # Check that fetch used the correct token
    auth_header = page.evaluate("window.lastFetchHeaders?.Authorization || window.lastFetchHeaders?.authorization")
    assert auth_header == 'Bearer my-test-token-123', "Fetch did not use the correct authorization header."

    # Clear localStorage and trigger non-interactively
    page.evaluate("localStorage.removeItem('HF_TOKEN')")
    page.evaluate("window.promptCalls = 0")
    page.evaluate("window.lastFetchHeaders = null")
    page.evaluate("state.aiCooldown = false")

    # Manually call askMistral directly for non-interactive test
    page.evaluate("askMistral('test non-interactive', false)")

    page.wait_for_timeout(500)

    # Check that prompt was not called
    prompt_calls_non_int = page.evaluate("window.promptCalls")
    assert prompt_calls_non_int == 0, "Prompt was incorrectly called in non-interactive mode."

    print("BYOK verification passed.")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_byok(page)
        finally:
            browser.close()

from playwright.sync_api import sync_playwright

def verify_ui():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Mock global state variables and Appwrite before the script runs to bypass auth flow
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } },
                Account: class { get() { return Promise.resolve({$id: "user1", name: "TestUser", email: "test@test.com"}); } },
                Databases: class {
                    listDocuments() {
                         return Promise.resolve({
                             documents: [
                                 {
                                     $id: "msg1",
                                     messageContent: "Hello world!",
                                     senderId: "TestUser",
                                     timestamp: new Date().toISOString(),
                                     isEdited: false
                                 }
                             ]
                         });
                    }
                },
                Storage: class {},
                ID: { unique: () => "id_" + Math.random() },
                Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
            };

            // Bypass fetch blocking for CDN scripts by mocking window.fetch completely
            // since we don't need real mistral/auth requests for this UI check
            const originalFetch = window.fetch;
            window.fetch = async (url, options) => {
                 if (typeof url === 'string' && url.includes('api-inference.huggingface.co')) {
                     return { ok: true, json: async () => [{generated_text: "Mock AI reply"}] };
                 }
                 return originalFetch(url, options);
            };

            // Override prompt to bypass BYOK
            window.prompt = () => "mock_token";
        """)

        # Go to the local page
        page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

        # Wait a moment for app initialization
        page.wait_for_timeout(2000)

        # Force show the app interface (bypassing landing)
        page.evaluate("if(typeof showApp === 'function') showApp();")

        # Wait a bit for messages and avatars to render
        page.wait_for_timeout(3000)

        # Take a screenshot
        page.screenshot(path="verification/avatar_verification.png")
        print("Screenshot saved to verification/avatar_verification.png")

        browser.close()

if __name__ == "__main__":
    verify_ui()

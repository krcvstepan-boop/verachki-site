from playwright.sync_api import sync_playwright

def verify_byok():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Mock Appwrite
        page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                    subscribe() { return {}; }
                },
                Account: class { get() { return Promise.reject("Mock User"); } },
                Databases: class {
                    listDocuments() { return Promise.resolve({documents: []}); }
                    createDocument() { return Promise.resolve({}); }
                },
                Storage: class { },
                ID: { unique: () => 'unique_id' },
                Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
            };
        """)

        # Mock fetch ROBUSTLY
        page.add_init_script("""
            window.originalFetch = window.fetch;
            window.fetch = async (input, init) => {
                let url = input;
                if (typeof input === 'object' && input !== null && input.url) {
                    url = input.url;
                }
                url = String(url || '');

                if (url.includes('mistral')) {
                    console.log("Mocking Mistral API call");
                    return {
                        ok: true,
                        status: 200,
                        json: async () => [{generated_text: "Mock AI Response"}]
                    };
                }
                console.log("Fetching other URL:", url);
                return { ok: false, status: 404 };
            };
        """)

        import os
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Wait for load
        page.wait_for_timeout(1000)

        # Handle dialog
        def handle_dialog(dialog):
            print(f"Dialog: {dialog.message}")
            dialog.accept("hf_testtoken123")
        page.on("dialog", handle_dialog)

        # Execute
        print("Calling askMistral...")
        try:
            page.evaluate("askMistral('test', true)")
        except Exception as e:
            print(f"Error during askMistral: {e}")

        # Verify Token
        token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        print(f"Stored Token: {token}")

        if token == "hf_testtoken123":
            print("SUCCESS: Token stored.")
        else:
            print(f"FAILURE: Token not stored.")
            exit(1)

        # Screenshot
        page.screenshot(path="verification/byok_verified.png")
        print("Screenshot saved.")

        browser.close()

if __name__ == "__main__":
    verify_byok()

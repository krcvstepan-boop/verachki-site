from playwright.sync_api import sync_playwright

def test_hf_token():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Mock APIs to prevent real calls
        page.route("**/*", lambda route: route.continue_())

        # Override Appwrite to prevent startup errors
        page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                },
                Account: class { get() { return Promise.reject(); } },
                Databases: class { listDocuments() { return Promise.resolve({documents: []}); } },
                Storage: class {},
                ID: { unique: () => '123' },
                Query: { equal: () => {}, limit: () => {}, orderAsc: () => {} }
            };
        """)

        # Start listening to dialogs before we trigger one
        dialog_messages = []
        def handle_dialog(dialog):
            dialog_messages.append(dialog.message)
            dialog.accept("MOCK_HF_TOKEN_12345")

        page.on("dialog", handle_dialog)

        # Intercept fetch to return mock mistral response
        page.route("**/api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", lambda route: route.fulfill(
            json=[{"generated_text": "Mock AI response"}]
        ))

        page.goto("http://localhost:8080/")

        # Ensure page is loaded
        page.wait_for_load_state("networkidle")

        # Trigger AI
        page.evaluate("""
            (async () => {
                localStorage.removeItem('HF_TOKEN'); // Ensure no token initially
                const res = await window.askMistral("Hello", true); // Should trigger prompt
                window.testResult = res;
            })()
        """)

        # Wait for test to complete
        page.wait_for_function("window.testResult !== undefined")
        result = page.evaluate("window.testResult")

        token = page.evaluate("localStorage.getItem('HF_TOKEN')")

        print(f"Dialog messages: {dialog_messages}")
        print(f"Stored token: {token}")
        print(f"AI response: {result}")

        assert len(dialog_messages) > 0, "Prompt was not triggered!"
        assert "Hugging Face Token" in dialog_messages[0], "Prompt message was incorrect!"
        assert token == "MOCK_HF_TOKEN_12345", "Token was not saved to localStorage!"
        assert result == "Mock AI response", "askMistral did not return expected mock text"

        print("SUCCESS! Token logic is verified.")
        browser.close()

if __name__ == "__main__":
    test_hf_token()

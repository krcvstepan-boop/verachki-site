from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Mock API to avoid actual external calls
        context = browser.new_context()
        page = context.new_page()

        # Mock Appwrite
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint(){return this;} setProject(){return this;} },
                Account: class { get() { return Promise.resolve({$id: '123', name: 'TestUser', email: 'test@test.com'}); } },
                Databases: class { listDocuments() { return Promise.resolve({documents: [{username: 'TestUser', rank: 'Наблюдатель'}]}); } },
                Storage: class {},
                ID: { unique: () => 'uid' },
                Query: { equal: () => {}, limit: () => {}, orderAsc: () => {} }
            };
        """)

        # Mock Hugging Face API
        page.route("https://api-inference.huggingface.co/**/*", lambda route: route.fulfill(
            status=200,
            json=[{"generated_text": "Mocked AI Response"}]
        ))

        page.goto("http://localhost:8080/index.html")
        page.wait_for_load_state("networkidle")

        # Bypass auth to get to chat interface
        page.evaluate("showApp()")
        page.wait_for_selector("#app-interface", state="visible")

        # Test 1: Direct trigger with no token (should prompt)
        print("Testing direct AI trigger without token...")

        # Setup a prompt handler
        dialog_handled = False
        def handle_dialog(dialog):
            nonlocal dialog_handled
            dialog_handled = True
            print(f"Dialog received: {dialog.message}")
            assert "Hugging Face Token" in dialog.message
            dialog.accept("mocked_test_token_123")

        page.on("dialog", handle_dialog)

        # Ensure localStorage is empty for HF_TOKEN
        page.evaluate("localStorage.removeItem('HF_TOKEN')")

        # Call the direct AI trigger
        page.evaluate("tryTriggerAI('система, привет')")

        page.wait_for_timeout(1000)

        # Verify dialog was handled
        assert dialog_handled, "Prompt for HF Token was not shown"

        # Verify token was saved
        saved_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        assert saved_token == "mocked_test_token_123", f"Token was not saved correctly. Got: {saved_token}"
        print("Test 1 Passed: Prompt shown and token saved.")

        page.screenshot(path="verification/verification.png")

        print("Verification complete.")
        browser.close()

if __name__ == "__main__":
    run()

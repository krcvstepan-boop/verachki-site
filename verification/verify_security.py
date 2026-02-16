from playwright.sync_api import sync_playwright
import os

def verify_security():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock Appwrite BEFORE page load to prevent errors
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() {} },
                Account: class { get() { return Promise.reject("Mock"); } createEmailPasswordSession() {} },
                Databases: class { listDocuments() { return Promise.resolve({documents:[]}); } },
                Storage: class {},
                ID: { unique: () => "mock-id" },
                Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
            };
        """)

        # Load file directly
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Check if HF_TOKEN is defined as a constant (it should NOT be)
        try:
            val = page.evaluate("HF_TOKEN")
            print(f"FAILURE: HF_TOKEN is still defined! Value: {val}")
        except Exception as e:
            if "HF_TOKEN is not defined" in str(e):
                print("SUCCESS: HF_TOKEN is not defined globally.")
            else:
                # In browser context, accessing undefined variable throws ReferenceError
                print(f"SUCCESS: HF_TOKEN access threw error as expected: {e}")

        # Test askMistral prompt
        dialog_message = []
        def handle_dialog(dialog):
            dialog_message.append(dialog.message)
            dialog.accept("hf_testtoken")

        page.on("dialog", handle_dialog)

        # Call askMistral interactively
        try:
            result = page.evaluate("""
                async () => {
                    localStorage.removeItem("HF_TOKEN");
                    // Mock fetch to avoid actual network call
                    const originalFetch = window.fetch;
                    window.fetch = async (url, options) => {
                         if (url.includes("huggingface")) {
                             if (options.headers.Authorization !== "Bearer hf_testtoken") {
                                 throw new Error("Wrong token in header: " + options.headers.Authorization);
                             }
                             return {
                                 ok: true,
                                 json: async () => ([{generated_text: "Mock response"}])
                             };
                         }
                         return originalFetch(url, options);
                    };
                    return await askMistral("test", true);
                }
            """)
            print(f"askMistral result: {result}")
        except Exception as e:
            print(f"FAILURE: askMistral execution failed: {e}")

        if dialog_message and "Введите ваш Hugging Face Token" in dialog_message[0]:
             print("SUCCESS: askMistral prompted for token.")
        else:
             print(f"FAILURE: askMistral did NOT prompt for token. Dialogs: {dialog_message}")

        # Check if token is saved
        saved_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        if saved_token == "hf_testtoken":
             print("SUCCESS: Token was saved to localStorage.")
        else:
             print(f"FAILURE: Token was NOT saved. Value: {saved_token}")

        browser.close()

if __name__ == "__main__":
    verify_security()

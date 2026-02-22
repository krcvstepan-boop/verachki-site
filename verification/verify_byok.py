from playwright.sync_api import sync_playwright
import os

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()
    page = context.new_page()

    # Mock Appwrite to avoid errors
    page.add_init_script("""
        window.Appwrite = {
            Client: class { setEndpoint(){ return this; } setProject(){ return this; } subscribe(){ return {}; } },
            Account: class { get(){ return Promise.reject(); } createEmailPasswordSession(){ return Promise.resolve(); } deleteSession(){ return Promise.resolve(); } },
            Databases: class { listDocuments(){ return Promise.resolve({documents: []}); } createDocument(){ return Promise.resolve({}); } updateDocument(){ return Promise.resolve({}); } deleteDocument(){ return Promise.resolve({}); } },
            Storage: class { createFile(){ return Promise.resolve({$id: 'file'}); } getFileView(){ return ''; } },
            ID: { unique: () => 'unique' },
            Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
        };
    """)

    # Load local file
    cwd = os.getcwd()
    page.goto(f'file://{cwd}/index.html')

    # Wait for script.js to load
    page.wait_for_timeout(1000)

    # 1. Test: Trigger AI interactively -> Should Prompt
    print("Testing Interactive Prompt...")

    # Setup dialog handler
    def handle_dialog(dialog):
        print(f"Dialog message: {dialog.message}")
        if "Hugging Face Token" in dialog.message:
            dialog.accept("my_fake_token_123")
        else:
            dialog.dismiss()

    page.on("dialog", handle_dialog)

    # Execute askMistral interactively
    result = page.evaluate("""
        async () => {
            // Clear storage first
            localStorage.clear();

            // Mock fetch to verify token was used
            window.lastToken = null;
            const originalFetch = window.fetch;
            window.fetch = async (url, options) => {
                if(url.includes('huggingface')) {
                    window.lastToken = options.headers.Authorization;
                    return { ok: true, json: async () => ([{ generated_text: "Success" }]) };
                }
                return { ok: false };
            };

            try {
                // Ensure askMistral is available
                if (typeof askMistral === 'undefined') return { error: "askMistral not found" };

                const res = await askMistral("test", true);
                return {
                    res: res,
                    tokenInStorage: localStorage.getItem('HF_TOKEN'),
                    tokenUsed: window.lastToken
                };
            } catch(e) {
                return { error: e.toString() };
            }
        }
    """)

    print(f"Result: {result}")

    if result.get('error'):
        print(f"❌ FAILURE: Script error: {result['error']}")
        exit(1)

    if result['tokenInStorage'] == "my_fake_token_123" and result['tokenUsed'] == "Bearer my_fake_token_123":
        print("✅ SUCCESS: Token prompted, saved, and used.")
    else:
        print("❌ FAILURE: Token verification failed.")
        exit(1)

    # Take screenshot just in case
    page.screenshot(path='verification/byok_check.png')

    browser.close()

if __name__ == "__main__":
    with sync_playwright() as playwright:
        run(playwright)

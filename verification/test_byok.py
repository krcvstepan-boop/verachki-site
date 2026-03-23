from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    page.add_init_script("""
        window.promptCalls = 0;
        window.prompt = function(text) {
            window.promptCalls++;
            return 'fake_token_123';
        };

        window.fetch = async function(url, options) {
            const parsedUrl = (url instanceof Request) ? url.url : url;
            if (parsedUrl === 'https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3') {
                const headers = options?.headers || (url instanceof Request ? Object.fromEntries(url.headers) : {});
                const authHeader = headers['Authorization'];
                if (authHeader === 'Bearer fake_token_123') {
                    return {
                        ok: true,
                        json: async () => [{ generated_text: 'Mocked AI response' }]
                    };
                }
                return {
                    ok: false,
                    status: 401,
                    json: async () => ({ error: 'Unauthorized' })
                };
            }
            return {ok: true, json: async () => ({documents: []})};
        };

        window.Appwrite = {
            Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() { return this; } },
            Account: class { get() { return Promise.resolve({ $id: 'user123', email: 'test@test.com' }); } createEmailSession() { return Promise.resolve({}); } },
            Databases: class { listDocuments() { return Promise.resolve({ documents: [] }); } createDocument() { return Promise.resolve({}); } },
            Storage: class {},
            ID: { unique: () => 'id' },
            Query: { orderDesc: () => {}, limit: () => {} }
        };
    """)

    page.goto("http://localhost:8080/index.html")

    page.evaluate("""
        window.db = { createDocument: () => Promise.resolve({}) };
        window.MSG_COL = 'msg';
        window.DB_ID = 'db';
        window.ID = { unique: () => 'id' };
        window.state = {
            aiCooldown: false
        };
    """)

    page.wait_for_timeout(1000)

    # Try triggering AI directly, should prompt for token and work
    page.evaluate("window.tryTriggerAI('Система, привет')")

    # wait a bit for async operations
    page.wait_for_timeout(1000)

    calls = page.evaluate("window.promptCalls")
    print(f"Prompt calls: {calls}")

    saved_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
    print(f"Saved token: {saved_token}")

    browser.close()

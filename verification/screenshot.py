from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()

    page.add_init_script("""
        window.promptCalls = 0;
        window.promptText = null;
        window.prompt = function(text) {
            window.promptCalls++;
            window.promptText = text;
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
    """)

    # block appwrite completely
    page.route("**/*", lambda route: route.continue_() if "localhost" in route.request.url or route.request.resource_type in ["document", "script", "stylesheet", "image"] else route.fulfill(status=200, json={}))

    page.goto("http://localhost:8080/index.html")

    page.evaluate("""
        window.Appwrite = {
            Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() { return this; } },
            Account: class { get() { return Promise.resolve({ $id: 'user123', email: 'test@test.com' }); } createEmailSession() { return Promise.resolve({}); } },
            Databases: class { listDocuments() { return Promise.resolve({ documents: [] }); } createDocument() { return Promise.resolve({}); } },
            Storage: class {},
            ID: { unique: () => 'id' },
            Query: { orderDesc: () => {}, limit: () => {} }
        };
        window.db = { createDocument: () => Promise.resolve({}) };
        window.MSG_COL = 'msg';
        window.DB_ID = 'db';
        window.ID = { unique: () => 'id' };
        window.state = {
            user: { $id: 'user123', email: 'test@test.com' },
            profile: { username: 'testuser', flower_xp: 0 },
            aiCooldown: false
        };
        window.account = new window.Appwrite.Account();
        window.client = new window.Appwrite.Client();
    """)

    page.wait_for_timeout(1000)

    # Show chat interface
    page.evaluate("""
        document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
        document.getElementById('app-interface').classList.remove('hidden');
    """)

    page.wait_for_timeout(500)

    # Trigger AI direct call
    page.evaluate("window.tryTriggerAI('Система, привет')")

    page.wait_for_timeout(1000)

    # Inject a div to show the prompt that was asked, to visually verify
    page.evaluate("""
        const div = document.createElement('div');
        div.style.position = 'fixed';
        div.style.top = '10px';
        div.style.left = '10px';
        div.style.backgroundColor = 'rgba(0,0,0,0.8)';
        div.style.color = 'lime';
        div.style.padding = '10px';
        div.style.zIndex = '9999';
        div.style.fontSize = '20px';
        div.innerHTML = `window.prompt was called with: <strong>${window.promptText}</strong><br>Token saved: <strong>${localStorage.getItem('HF_TOKEN')}</strong>`;
        document.body.appendChild(div);
    """)

    page.screenshot(path="verification/screenshot.png")
    browser.close()

from playwright.sync_api import sync_playwright
import sys

def verify_byok():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Block external CDNs to avoid timeouts
        context.route("**/*", lambda route: route.continue_() if "localhost" in route.request.url or "127.0.0.1" in route.request.url else route.abort())

        # Mock Appwrite and set global state
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() { return this; } },
                Account: class { get() { return Promise.resolve({ $id: 'test-user', name: 'Test User', email: 'test@example.com' }); } },
                Databases: class {
                    listDocuments() { return Promise.resolve({ documents: [{ $id: 'test-profile', username: 'Test User', rank: 'Наблюдатель', ether: 0, flower_xp: 0 }] }); }
                    createDocument() { return Promise.resolve({ $id: 'msg-id', messageContent: 'Test', senderId: 'СИСТЕМА', timestamp: new Date().toISOString(), isEdited: false }); }
                },
                Storage: class { getFileView() { return ''; } },
                ID: { unique: () => 'unique-id' },
                Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
            };
            window.countdownInterval = null;
            window.countdownAnimFrame = null;

            // Override window.prompt
            window.promptCalls = 0;
            window.prompt = function(message) {
                window.promptCalls++;
                return "hf_mock_token_from_prompt";
            };
        """)

        # Navigate to the local server
        page.goto("http://localhost:8080/index.html", wait_until='domcontentloaded')

        # We need to completely mock window.fetch for HuggingFace to bypass CORS entirely in Playwright context
        page.evaluate("""
            window.hf_fetch_calls = window.hf_fetch_calls || [];
            const originalFetch = window.fetch;
            window.fetch = async function(url, options) {
                if (url instanceof Request) {
                     if(url.url.includes('api-inference.huggingface.co')) {
                         window.hf_fetch_calls.push(url.headers.get('Authorization'));
                         return {
                            ok: true,
                            status: 200,
                            json: () => Promise.resolve([{"generated_text": "Mocked AI response"}])
                        };
                     }
                } else if (typeof url === 'string' && url.includes('api-inference.huggingface.co')) {
                    window.hf_fetch_calls.push(options ? (options.headers ? options.headers.Authorization : null) : null);
                    return {
                        ok: true,
                        status: 200,
                        json: () => Promise.resolve([{"generated_text": "Mocked AI response"}])
                    };
                }
                return originalFetch.apply(this, arguments);
            };
        """)

        # Trigger showApp to bypass auth screen and initialize chat interface
        page.evaluate("if(typeof showApp === 'function') showApp();")

        # Wait a moment for app interface to be visible
        page.wait_for_timeout(1000)

        # Clear localStorage HF_TOKEN to simulate first run
        page.evaluate("localStorage.removeItem('HF_TOKEN');")

        # Expose a function to track fetch calls to Hugging Face
        fetch_calls = []

        # We need to temporarily un-abort external calls so our huggingface mock works
        context.unroute("**/*")

        context.route("**/*", lambda route: route.continue_() if "localhost" in route.request.url or "127.0.0.1" in route.request.url else route.abort())

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        # Call tryTriggerAI directly (simulating a direct call which passes isInteractive=true)
        # using the Appwrite mock to satisfy the createDocument call
        page.evaluate("""
            window.db = new window.Appwrite.Databases(new window.Appwrite.Client());
            window.DB_ID = 'test-db';
            window.MSG_COL = 'test-col';
            tryTriggerAI('система, привет').catch(e => console.error(e));
        """)

        # Wait for the AI call to process
        page.wait_for_timeout(2000)

        # Check if prompt was called
        prompt_calls = page.evaluate("window.promptCalls")
        print(f"window.prompt calls: {prompt_calls}")
        if prompt_calls == 0:
            print("FAILURE: window.prompt was not called when token was missing.")
            sys.exit(1)

        # Check if token was saved to localStorage
        saved_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        print(f"Saved token in localStorage: {saved_token}")
        if saved_token != "hf_mock_token_from_prompt":
            print("FAILURE: Token from prompt was not saved to localStorage.")
            sys.exit(1)

        # Check if the correct authorization header was sent
        fetch_calls = page.evaluate("window.hf_fetch_calls || []")
        print(f"Fetch calls to HF: {len(fetch_calls)}")
        if len(fetch_calls) > 0:
            auth_header = fetch_calls[0]
            print(f"Auth header sent: {auth_header}")
            if auth_header != "Bearer hf_mock_token_from_prompt":
                print("FAILURE: Incorrect authorization header sent.")
                sys.exit(1)
        else:
            print("FAILURE: No fetch call made to Hugging Face API.")
            sys.exit(1)

        print("SUCCESS: BYOK flow verified successfully.")

        # Capture a screenshot of the chat interface (might not show much for background AI call, but good for verification)
        page.screenshot(path="verification/byok_screenshot.png")

        browser.close()

if __name__ == "__main__":
    verify_byok()

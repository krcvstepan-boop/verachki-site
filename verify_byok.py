import asyncio
from playwright.async_api import async_playwright
import os

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()

        # Block external requests to avoid timeouts/CORS issues during test
        await context.route("**/*", lambda route: route.continue_() if "localhost" in route.request.url or route.request.url.startswith("file://") else route.abort())

        page = await context.new_page()

        # Mock window.prompt and localStorage
        await page.add_init_script("""
            window.promptCount = 0;
            window.promptArgs = [];
            window.prompt = function(message) {
                window.promptCount++;
                window.promptArgs.push(message);
                return 'mock_token_123';
            };

            // Mock fetch to avoid real API calls and simulate responses
            window.originalFetch = window.fetch;
            window.fetchCount = 0;
            window.fetchTokens = [];
            window.fetch = async function(url, options) {
                if (url.includes('api-inference.huggingface.co')) {
                    window.fetchCount++;
                    const authHeader = options?.headers?.Authorization || options?.headers?.get('Authorization');
                    if (authHeader) {
                        window.fetchTokens.push(authHeader);
                    }
                    return new Response(JSON.stringify([{ generated_text: "Mock AI Response" }]), {
                        status: 200,
                        headers: { 'Content-Type': 'application/json' }
                    });
                }
                return window.originalFetch(url, options);
            };

            // Mock Appwrite to bypass auth and initialization issues
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } },
                Account: class { get() { return Promise.resolve({ $id: 'user1', name: 'TestUser', email: 'test@test.com' }); } },
                Databases: class {
                    listDocuments() { return Promise.resolve({ documents: [{ $id: 'prof1', username: 'TestUser', email: 'test@test.com', rank: 'User', about: '', ether: 0, flower_xp: 0 }] }); }
                    createDocument() { return Promise.resolve({}); }
                },
                Storage: class {},
                ID: { unique: () => 'id123' },
                Query: { equal: () => '', orderAsc: () => '', limit: () => '' }
            };

            // Allow App to show
            window.onload = () => {
                if(window.showApp) window.showApp();
            };
        """)

        # Go to local server
        await page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

        # Test 1: Direct Call (isInteractive = true)
        print("Testing Direct Call...")
        await page.evaluate("tryTriggerAI('ии, привет')")

        # Give it a moment to process the async call
        await page.wait_for_timeout(500)

        prompt_count = await page.evaluate("window.promptCount")
        fetch_count = await page.evaluate("window.fetchCount")
        tokens_used = await page.evaluate("window.fetchTokens")
        stored_token = await page.evaluate("localStorage.getItem('HF_TOKEN')")

        print(f"Prompt Count: {prompt_count}")
        print(f"Fetch Count: {fetch_count}")
        print(f"Token used in fetch: {tokens_used[0] if tokens_used else 'None'}")
        print(f"Stored Token: {stored_token}")

        assert prompt_count == 1, "Prompt should have been called once for direct interaction."
        assert fetch_count == 1, "Fetch to Hugging Face should have been called."
        assert "mock_token_123" in tokens_used[0], "The mock token should have been sent in the Authorization header."
        assert stored_token == "mock_token_123", "The token should have been saved to localStorage."

        # Test 2: Random Trigger without token (isInteractive = false)
        print("\nTesting Random Trigger (cooldown bypass via reset)...")
        # Clear token and reset cooldown
        await page.evaluate("localStorage.removeItem('HF_TOKEN'); state.aiCooldown = false; window.promptCount = 0; window.fetchCount = 0;")

        # Force a random trigger (we replace Math.random temporarily to guarantee trigger)
        await page.evaluate("""
            const oldRandom = Math.random;
            Math.random = () => 0.01; // Force < 0.05
            tryTriggerAI('just a normal message');
            Math.random = oldRandom;
        """)

        await page.wait_for_timeout(500)

        prompt_count_2 = await page.evaluate("window.promptCount")
        fetch_count_2 = await page.evaluate("window.fetchCount")
        stored_token_2 = await page.evaluate("localStorage.getItem('HF_TOKEN')")

        print(f"Prompt Count (Random Trigger): {prompt_count_2}")
        print(f"Fetch Count (Random Trigger): {fetch_count_2}")
        print(f"Stored Token (Random Trigger): {stored_token_2}")

        assert prompt_count_2 == 0, "Prompt should NOT be called for non-interactive (random) triggers."
        assert fetch_count_2 == 0, "Fetch should not happen if token is missing and interactive prompt is skipped."
        assert stored_token_2 is None, "Token should not be set."

        # Test 3: 401 Unauthorized Error Handling
        print("\nTesting 401 Error Handling...")
        await page.evaluate("""
            localStorage.setItem('HF_TOKEN', 'bad_token');
            state.aiCooldown = false;

            // Modify mock fetch to return 401
            window.fetch = async function(url, options) {
                if (url && url.includes && url.includes('api-inference.huggingface.co')) {
                    return new Response(JSON.stringify({ error: "Unauthorized" }), {
                        status: 401,
                        headers: { 'Content-Type': 'application/json' }
                    });
                }
                return window.originalFetch(url, options);
            };
        """)

        # The prompt will try to trigger AI, it should get 401, clear token, and throw error
        try:
            # We use askMistral directly here to catch the error easier
            await page.evaluate("askMistral('test error handling', false)")
        except Exception as e:
             # Evaluating throws error to playwright if we don't catch it inside evaluate,
             # but askMistral catches internally and returns null, logging the error.
             pass

        await page.wait_for_timeout(500)

        stored_token_3 = await page.evaluate("localStorage.getItem('HF_TOKEN')")
        print(f"Stored Token after 401: {stored_token_3}")

        assert stored_token_3 is None, "Token should be removed from localStorage upon 401 response."

        print("\nAll BYOK verification tests passed successfully!")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())

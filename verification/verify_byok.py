
import asyncio
import os
from playwright.async_api import async_playwright

async def verify_byok():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Route requests to Hugging Face to our mock handler
        token_used = None

        async def handle_hf_request(route):
            nonlocal token_used
            headers = route.request.headers
            token_used = headers.get("authorization")
            print(f"DEBUG: Intercepted HF request. Auth header: {token_used}")
            await route.fulfill(
                status=200,
                body='[{"generated_text": "I am a secure AI."}]',
                headers={"content-type": "application/json"}
            )

        await page.route("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", handle_hf_request)

        # Mock prompt and localStorage - FIX: Ensure prompt mock works
        await page.add_init_script("""
            // Force override prompt
            Object.defineProperty(window, 'prompt', {
                writable: true,
                configurable: true,
                value: function(msg, defaultVal) {
                    console.log('Prompt triggered:', msg);
                    return 'mock_hf_token_123';
                }
            });
            // Clear storage at start
            localStorage.clear();
        """)

        # Load the page
        cwd = os.getcwd()
        await page.goto(f"file://{cwd}/index.html")
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1000)

        # --- TEST 1: Interactive Call ---
        print("\n--- TEST 1: Interactive Call ---")

        # Verify prompt mock
        prompt_val = await page.evaluate("window.prompt('test')")
        print(f"DEBUG: Prompt check returns: {prompt_val}")

        if prompt_val != 'mock_hf_token_123':
             print("❌ FAIL: Prompt mock is not working!")
             # Try to re-apply mock
             await page.evaluate("""
                window.prompt = function(msg) { return 'mock_hf_token_123'; };
             """)

        # Execute askMistral
        result = await page.evaluate("""
            (async () => {
                try {
                    if (typeof askMistral === 'undefined') return 'UNDEFINED';
                    // Force interactive
                    await askMistral('test', true);
                    return 'SUCCESS';
                } catch (e) {
                    return 'ERROR: ' + e.toString();
                }
            })()
        """)
        print(f"JS Execution Result: {result}")

        # Wait a bit
        await page.wait_for_timeout(1000)

        # Check LocalStorage
        saved_token = await page.evaluate("localStorage.getItem('HF_TOKEN')")
        print(f"Token in localStorage: {saved_token}")

        if saved_token == 'mock_hf_token_123':
            print("✅ PASS: Token saved to localStorage.")
        else:
             print("❌ FAIL: Token not saved.")

        # --- TEST 2: Background Call ---
        print("\n--- TEST 2: Background Call (No Token) ---")

        await page.evaluate("localStorage.removeItem('HF_TOKEN')")
        token_used = None

        # Mock prompt to throw error
        await page.evaluate("""
            window.prompt = function() { throw new Error("PROMPT_CALLED_IN_BACKGROUND"); };
        """)

        try:
            # Call askMistral directly with isInteractive=false (default)
            await page.evaluate("""
                (async () => {
                     if (typeof askMistral !== 'undefined') {
                         await askMistral('bg_test');
                     }
                })()
            """)
            await page.wait_for_timeout(1000)

            # If no error thrown, we are good.
            if token_used is None:
                print("✅ PASS: No prompt error and no request sent.")
            else:
                print(f"❌ FAIL: Request sent! {token_used}")

        except Exception as e:
            if "PROMPT_CALLED_IN_BACKGROUND" in str(e):
                 print("❌ FAIL: Prompt was called!")
            else:
                 print(f"❌ FAIL: Unexpected error: {e}")

        # --- TEST 3: Stored Token ---
        print("\n--- TEST 3: Stored Token Usage ---")
        await page.evaluate("localStorage.setItem('HF_TOKEN', 'stored_abc')")

        # Restore prompt mock to be safe
        await page.evaluate("window.prompt = function() { return 'unexpected'; };")

        token_used = None
        await page.evaluate("""
             (async () => {
                 if (typeof askMistral !== 'undefined') {
                     await askMistral('stored_test');
                 }
            })()
        """)
        await page.wait_for_timeout(1000)

        if token_used == "Bearer stored_abc":
             print("✅ PASS: Stored token used.")
        else:
             print(f"❌ FAIL: Token not used. Header: {token_used}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_byok())

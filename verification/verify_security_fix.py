import sys
import os
from playwright.sync_api import sync_playwright

def verify_fix():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the page
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Mock fetch to intercept the AI call
        page.evaluate("""
            window.lastFetchHeaders = null;
            window.originalFetch = window.fetch;
            window.fetch = async (input, init) => {
                let url = input;
                if (typeof input === 'object' && input !== null && input.url) {
                    url = input.url;
                }

                if (url && typeof url === 'string' && url.includes("huggingface")) {
                    window.lastFetchHeaders = init ? init.headers : {};
                    return {
                        ok: true,
                        json: async () => [{ generated_text: "AI Response" }]
                    };
                }
                // Mock other fetches to avoid errors
                return { ok: true, json: async () => ({}) };
            };
        """)

        # Wait a bit for scripts to load
        page.wait_for_timeout(1000)

        # Check if setAIToken exists
        is_fixed = page.evaluate("typeof window.setAIToken === 'function'")

        if not is_fixed:
            print("Pre-fix state detected: window.setAIToken not found.")

            # Check if askMistral is accessible
            can_call_ai = page.evaluate("typeof window.askMistral === 'function'")
            if can_call_ai:
                print("Calling askMistral to check for hardcoded token...")
                try:
                    page.evaluate("window.askMistral('test')")
                    # Give it a moment
                    page.wait_for_timeout(500)
                    auth_header = page.evaluate("window.lastFetchHeaders ? window.lastFetchHeaders.Authorization : null")
                    print(f"Current Authorization Header: {auth_header}")

                    if auth_header and "Bearer hf_" in auth_header:
                        print("CONFIRMED: Hardcoded token is currently being used.")
                    else:
                        print("WARNING: Could not verify hardcoded token usage (maybe fetch wasn't called?).")
                except Exception as e:
                    print(f"Error calling askMistral: {e}")
            else:
                print("askMistral is not globally accessible.")

            browser.close()
            return

        print("Post-fix state detected: window.setAIToken exists.")

        # Test 1: No Token
        print("Test 1: Calling askMistral with NO token...")
        page.evaluate("localStorage.removeItem('HF_TOKEN')")
        response = page.evaluate("window.askMistral('test')")

        if response is None:
            print("SUCCESS: askMistral returned null as expected.")
        else:
            print(f"FAILURE: askMistral returned '{response}' despite no token.")
            sys.exit(1)

        # Test 2: Set Token
        print("Test 2: Setting token via window.setAIToken...")
        test_token = "TEST_TOKEN_SECURE_123"
        page.evaluate(f"window.setAIToken('{test_token}')")

        # Verify it's in localStorage
        stored = page.evaluate("localStorage.getItem('HF_TOKEN')")
        if stored != test_token:
            print(f"FAILURE: Token not saved to localStorage. Got {stored}")
            sys.exit(1)

        # Test 3: Call AI with Token
        print("Test 3: Calling askMistral WITH token...")
        page.evaluate("window.askMistral('test')")

        # Get headers from the intercepted fetch
        auth_header = page.evaluate("window.lastFetchHeaders ? window.lastFetchHeaders.Authorization : null")

        expected_header = f"Bearer {test_token}"
        if auth_header == expected_header:
            print(f"SUCCESS: Authorization header matches: {auth_header}")
        else:
            print(f"FAILURE: Authorization header mismatch. Expected '{expected_header}', Got '{auth_header}'")
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    verify_fix()

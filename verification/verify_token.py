import os
import time
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load the page
        page.goto(f"file://{os.path.abspath('index.html')}")

        # Wait for script.js to load (defer)
        page.wait_for_load_state('networkidle')

        # 1. Test: No Token -> Returns null
        print("Testing askMistral with no token...")

        # Ensure token is clear
        page.evaluate("localStorage.removeItem('HF_TOKEN')")

        # Call askMistral
        result = page.evaluate("window.askMistral ? window.askMistral('hello') : 'FUNCTION_NOT_FOUND'")

        if result == 'FUNCTION_NOT_FOUND':
            print("ERROR: askMistral function not found on window object.")
        elif result is None:
            print("SUCCESS: askMistral returned null when no token is present.")
        else:
            print(f"FAILURE: askMistral returned {result} instead of null.")
            exit(1)

        # 2. Test: With Token -> Calls fetch with correct header
        print("Testing askMistral with token...")

        test_token = "hf_test_token_123"
        page.evaluate(f"window.setAIToken('{test_token}')")

        # Verify token is in localStorage
        stored_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        if stored_token != test_token:
            print("FAILURE: setAIToken did not set localStorage correctly.")
            exit(1)

        # Mock ALL fetches to prevent network errors
        page.evaluate("""
            window.lastFetchHeaders = null;
            window.fetch = async (url, options) => {
                let urlStr = url;
                try {
                    if (typeof url === 'object' && url instanceof URL) {
                        urlStr = url.toString();
                    } else if (typeof url === 'object' && url instanceof Request) {
                         urlStr = url.url;
                    }
                } catch (e) {}

                if (urlStr && typeof urlStr === 'string' && urlStr.includes('mistralai')) {
                     window.lastFetchHeaders = options ? options.headers : {};
                     return {
                        ok: true,
                        json: async () => [{ generated_text: "I am AI." }]
                     };
                }

                // Return dummy response for everything else
                return {
                    ok: true,
                    json: async () => ({}),
                    text: async () => "",
                    blob: async () => new Blob([])
                };
            };
        """)

        # Call askMistral again
        print("Calling askMistral...")
        # Since we mocked fetch, it should succeed
        response_text = page.evaluate("window.askMistral('hello again')")
        print(f"askMistral response: {response_text}")

        # Check headers
        headers = page.evaluate("window.lastFetchHeaders")

        if not headers:
            print("FAILURE: Fetch was not called.")
            exit(1)

        auth_header = headers.get('Authorization')
        if auth_header == f"Bearer {test_token}":
            print(f"SUCCESS: Authorization header is correct: {auth_header}")
        else:
            print(f"FAILURE: Authorization header mismatch. Got: {auth_header}")
            exit(1)

        browser.close()

if __name__ == "__main__":
    run()

import json
import os
from playwright.sync_api import sync_playwright

def verify_byok():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Mock huggingface API to test authorization header
        def mock_hf_route(route):
            request = route.request
            auth_header = request.headers.get("authorization")
            print(f"Intercepted Request to HF with auth header: {auth_header}")
            assert auth_header == "Bearer test_token_from_prompt", f"Expected 'Bearer test_token_from_prompt', got {auth_header}"

            # Send a fake response
            route.fulfill(
                status=200,
                content_type="application/json",
                body=json.dumps([{"generated_text": "Mocked response from Verachka"}])
            )

        context.route("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", mock_hf_route)

        # Don't block all traffic, just external APIs if they hang. Let's let normal traffic through.
        # But we DO want to block appwrite so it doesn't hang on auth checking, and just mock state
        def block_appwrite(route):
            print(f"Blocking appwrite request to {route.request.url}")
            route.fulfill(status=200, content_type="application/json", body="{}")

        context.route("https://fra.cloud.appwrite.io/**/*", block_appwrite)

        page = context.new_page()

        # Mock window.prompt to return our test token
        page.add_init_script("""
            window.prompt = function(message) {
                console.log("Prompt intercepted: " + message);
                return "test_token_from_prompt";
            };
        """)

        # Go to local server
        print("Loading local server...")
        page.goto("http://localhost:8080")

        # Wait a bit for initialization
        page.wait_for_timeout(1000)

        # Trigger askMistral with interactive=True
        print("Testing askMistral (interactive)...")
        result = page.evaluate("""
            async () => {
                // Clear any existing token to force prompt
                localStorage.removeItem('HF_TOKEN');
                return await askMistral("Hello Verachka", true);
            }
        """)

        assert result == "Mocked response from Verachka", f"Expected 'Mocked response from Verachka', got {result}"
        print(f"askMistral Success: {result}")

        # Ensure the token was saved in localStorage
        saved_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        assert saved_token == "test_token_from_prompt", f"Token not saved to localStorage. Expected 'test_token_from_prompt', got {saved_token}"
        print(f"localStorage token verified: {saved_token}")

        # Test the unauthorized case
        def mock_hf_401(route):
            print("Intercepting HF 401 error response")
            route.fulfill(
                status=401,
                content_type="application/json",
                body='{"error": "Unauthorized"}'
            )

        context.unroute("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3")
        context.route("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", mock_hf_401)

        # We evaluate it and expect an error/null
        print("Testing askMistral (401 handling)...")
        error_result = page.evaluate("""
            async () => {
                // Token is still in localStorage from previous step
                return await askMistral("Hello again", false);
            }
        """)
        assert error_result is None, "Expected askMistral to return null on error"

        # Verify the token was removed
        cleared_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        assert cleared_token is None, "Token was not cleared from localStorage after 401"
        print("localStorage token cleared successfully after 401 error")

        print("BYOK Verification Passed!")

        # Take a screenshot to show the app state
        page.screenshot(path="verification/byok_screenshot.png")

        context.close()
        browser.close()

if __name__ == "__main__":
    verify_byok()

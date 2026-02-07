from playwright.sync_api import sync_playwright
import sys

def verify_token_logic():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock fetch to intercept Mistral calls
        page.route("**/mistralai/**", lambda route: route.fulfill(
            status=200,
            body='[{"generated_text": "I am a secure AI."}]',
            headers={"Content-Type": "application/json"}
        ))

        # Navigate to the page
        print("Navigating to http://localhost:8080/index.html")
        page.goto("http://localhost:8080/index.html")

        # Wait for scripts to load
        page.wait_for_timeout(1000)

        # 1. Verify getHFToken exists and returns null initially
        try:
            token = page.evaluate("typeof getHFToken === 'function' ? getHFToken() : 'MISSING'")
            if token is None:
                print("SUCCESS: getHFToken() returned null initially.")
            elif token == 'MISSING':
                print("FAILURE: getHFToken function not found.")
                sys.exit(1)
            else:
                print(f"FAILURE: getHFToken() returned {token} initially (should be null).")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        # 2. Verify setAIToken works
        try:
            page.evaluate("window.setAIToken('test-secret-token')")
            token_after = page.evaluate("getHFToken()")
            if token_after == 'test-secret-token':
                print("SUCCESS: setAIToken() correctly set the token.")
            else:
                print(f"FAILURE: getHFToken() returned {token_after} after setting (expected 'test-secret-token').")
                sys.exit(1)
        except Exception as e:
            print(f"ERROR: {e}")
            sys.exit(1)

        # 3. Verify askMistral uses the token
        # We trigger askMistral and check the request headers by intercepting

        request_captured = False
        def handle_request(route):
            nonlocal request_captured
            headers = route.request.headers
            auth = headers.get('authorization', '') or headers.get('Authorization', '')
            if auth == 'Bearer test-secret-token':
                print("SUCCESS: askMistral used the correct Authorization header.")
                request_captured = True
            else:
                print(f"FAILURE: askMistral used header: {auth}")
            route.fulfill(body='[{"generated_text": "OK"}]')

        page.unroute("**/mistralai/**") # Clear previous route
        page.route("**/mistralai/**", handle_request)

        # Call askMistral
        page.evaluate("askMistral('Hello')")
        page.wait_for_timeout(1000)

        if not request_captured:
            print("FAILURE: askMistral request not captured or incorrect header.")
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    verify_token_logic()

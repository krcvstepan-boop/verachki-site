import os
from playwright.sync_api import sync_playwright

def verify_byok():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Load the page
        page.goto(f"file://{os.getcwd()}/index.html")

        # 1. Verify that hardcoded keys are gone (static analysis of loaded script)
        content = page.content()
        if "hf_UwcAeGYbQKgyWa" in content or "AlccfNJwQoCAxVzHgSdS" in content:
            print("FAILURE: Hardcoded keys still found in source!")
            return False
        else:
            print("SUCCESS: Hardcoded keys removed.")

        # 2. Mock window.prompt to return a test token
        test_token = "hf_test_token_123"

        # We need to inject a script to mock prompt because page.on('dialog') handles it differently
        # But actually, let's use page.evaluate to overwrite prompt if needed,
        # or rely on page.on('dialog', lambda dialog: dialog.accept(test_token))

        # Setup dialog handler
        def handle_dialog(dialog):
            print(f"Dialog opened: {dialog.message}")
            dialog.accept(test_token)

        page.on("dialog", handle_dialog)

        # 3. Simulate triggering AI (which should prompt for key)
        # We can call askMistral directly via evaluate
        print("Simulating askMistral call without token...")

        # Mock fetch to avoid actual network call and return success/failure
        page.route("**/api-inference.huggingface.co/**", lambda route: route.fulfill(
            status=200,
            body='[{"generated_text": "I am a test AI."}]',
            headers={"Content-Type": "application/json"}
        ))

        # We need to make sure askMistral is accessible. It is in script.js which is deferred.
        # Wait for load.
        page.wait_for_load_state("networkidle")

        # Clear local storage first just in case
        page.evaluate("localStorage.removeItem('HF_TOKEN')")

        # Call askMistral interactively
        result = page.evaluate("askMistral('Hello', true)")
        print(f"Result from first call: {result}")

        # Verify token is saved
        saved_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        if saved_token == test_token:
            print("SUCCESS: Token saved to localStorage.")
        else:
            print(f"FAILURE: Token not saved. Found: {saved_token}")
            return False

        # 4. Simulate 401 Error to verify token clearing
        print("Simulating 401 Unauthorized...")
        page.route("**/api-inference.huggingface.co/**", lambda route: route.fulfill(
            status=401,
            body='{"error": "Unauthorized"}'
        ))

        # Call again (non-interactive this time to just trigger the error handler)
        # Or interactive, doesn't matter, we want to see if it clears the token
        page.evaluate("askMistral('Hello', true)")

        # Check if token is cleared
        saved_token_after = page.evaluate("localStorage.getItem('HF_TOKEN')")
        if saved_token_after is None:
            print("SUCCESS: Token cleared on 401.")
        else:
            print(f"FAILURE: Token NOT cleared on 401. Found: {saved_token_after}")
            return False

        browser.close()
        return True

if __name__ == "__main__":
    if verify_byok():
        print("ALL SECURITY CHECKS PASSED")
        exit(0)
    else:
        print("SECURITY CHECKS FAILED")
        exit(1)

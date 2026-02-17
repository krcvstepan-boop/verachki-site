import re
import os
from playwright.sync_api import sync_playwright

def verify_security():
    # 1. Check for hardcoded token in script.js
    print("Checking for hardcoded secrets...")
    with open('script.js', 'r', encoding='utf-8') as f:
        content = f.read()

    # The actual key parts found earlier
    key_part_1 = "hf_UwcAeGYbQKgyWa"
    key_part_2 = "AlccfNJwQoCAxVzHgSdS"

    if key_part_1 in content or key_part_2 in content:
        print("FAILURE: Hardcoded HF_TOKEN found in script.js!")
        # We don't exit here because we want to test the dynamic behavior too (which will likely fail if code isn't updated)
    else:
        print("SUCCESS: Hardcoded HF_TOKEN removed from script.js.")

    # 2. Verify Dynamic Behavior (Prompt on missing token)
    print("Verifying BYOK behavior...")
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            context = browser.new_context()
            page = context.new_page()

            # Mock Appwrite (prevent actual network calls that might fail or be slow)
            page.route("**/*", lambda route: route.continue_())

            # Load the page (local file)
            page.goto("file://" + os.path.abspath("index.html"))

            # Clear localStorage to simulate fresh user
            page.evaluate("localStorage.clear()")

            # Setup dialog handler
            dialog_triggered = False
            def handle_dialog(dialog):
                nonlocal dialog_triggered
                print(f"Dialog triggered: {dialog.message}")
                dialog_triggered = True
                dialog.accept("hf_test_token_123")

            page.on("dialog", handle_dialog)

            # Trigger askMistral interactively
            # We need to wait for script.js to load. It's defer, so explicit wait or check.
            page.wait_for_load_state("networkidle")

            # Direct call to askMistral with interactive=true
            # Note: askMistral is async
            result = page.evaluate("""async () => {
                if (typeof askMistral === 'function') {
                    return await askMistral('test prompt', true);
                }
                return 'FUNCTION_MISSING';
            }""")

            if result == 'FUNCTION_MISSING':
                 print("FAILURE: askMistral function not found.")
            elif dialog_triggered:
                print("SUCCESS: Prompt was triggered for missing token.")

                # Check if token was saved
                token = page.evaluate("localStorage.getItem('HF_TOKEN')")
                if token == "hf_test_token_123":
                    print("SUCCESS: Token saved to localStorage.")
                else:
                    print(f"FAILURE: Token not saved. Found: {token}")
            else:
                print("FAILURE: No prompt triggered when calling askMistral(..., true) without token.")

            browser.close()

    except Exception as e:
        print(f"ERROR during verification: {e}")

if __name__ == "__main__":
    verify_security()

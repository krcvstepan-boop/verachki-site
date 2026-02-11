from playwright.sync_api import sync_playwright
import os

def verify_security():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load the page from file (assuming verification runs from root)
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")
        page.wait_for_load_state("networkidle")

        print("Page loaded.")

        # 1. Check for hardcoded secrets in source
        content = page.content()
        if "hf_UwcAeGYbQKgyWa" in content or "AlccfNJwQoCAxVzHgSdS" in content:
            print("FAILURE: Hardcoded API key found in page source!")
            browser.close()
            exit(1)
        else:
            print("SUCCESS: Hardcoded API key NOT found in source.")

        # 2. Check global variables
        hf_token_defined = page.evaluate("() => typeof HF_TOKEN !== 'undefined'")
        if hf_token_defined:
            print("FAILURE: HF_TOKEN global variable is still defined!")
            browser.close()
            exit(1)
        else:
            print("SUCCESS: HF_TOKEN is undefined.")

        # 3. Check new functions exist
        funcs_exist = page.evaluate("() => typeof getAIToken === 'function' && typeof setAIToken === 'function'")
        if not funcs_exist:
             print("FAILURE: New BYOK functions (getAIToken, setAIToken) not found!")
             browser.close()
             exit(1)
        else:
             print("SUCCESS: BYOK functions found.")

        # 4. Verify behavior: askMistral without token (non-interactive) should return null
        # We need to wait for script.js to fully load if it's deferred.
        # But we waited for networkidle.

        print("Testing askMistral behavior...")
        result = page.evaluate("async () => await askMistral('test', false)")
        if result is None:
            print("SUCCESS: askMistral(..., false) returned null when token is missing.")
        else:
            print(f"FAILURE: askMistral returned {result} instead of null.")
            browser.close()
            exit(1)

        browser.close()

if __name__ == "__main__":
    verify_security()

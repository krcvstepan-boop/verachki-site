import os
from playwright.sync_api import sync_playwright

def verify_byok():
    cwd = os.getcwd()
    file_url = f"file://{cwd}/index.html"

    with sync_playwright() as p:
        # Launch with args to disable web security to bypass CORS for file:// protocol testing
        browser = p.chromium.launch(headless=True, args=["--disable-web-security"])
        context = browser.new_context()
        page = context.new_page()

        print("Checking script.js for leaked keys...")
        with open("script.js", "r") as f:
            content = f.read()
            if "hf_UwcAeGYbQKgyWa" in content or "AlccfNJwQoCAxVzHgSdS" in content:
                print("FAILURE: Hardcoded keys still present in script.js")
                exit(1)
            else:
                print("SUCCESS: Hardcoded keys removed from script.js")

        print(f"Loading {file_url}")

        # Monitor console
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}") if "Error" in msg.text or "warn" in msg.type else None)

        def handle_dialog(dialog):
            if "Hugging Face Token" in dialog.message:
                dialog.accept("hf_TEST_KEY_123")
                print("Dialog accepted with test key.")
            else:
                dialog.dismiss()

        page.on("dialog", handle_dialog)

        try:
            page.goto(file_url)
            page.wait_for_load_state("domcontentloaded")
            page.wait_for_timeout(2000)

            # Clean start
            page.evaluate("localStorage.removeItem('HF_TOKEN')")

            print("Triggering askMistral interactively...")

            def handle_route_success(route):
                if route.request.method == "OPTIONS":
                    route.fulfill(status=200, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "Authorization, Content-Type"})
                else:
                    route.fulfill(status=200, content_type="application/json", body='[{"generated_text": " I am AI."}]', headers={"Access-Control-Allow-Origin": "*"})

            page.route("**huggingface.co**", handle_route_success)

            result = page.evaluate("askMistral('Hello', true)")

            token = page.evaluate("localStorage.getItem('HF_TOKEN')")
            if token == "hf_TEST_KEY_123":
                print("SUCCESS: Token saved to localStorage after prompt.")
            else:
                print(f"FAILURE: Token not saved. Found: {token}")
                exit(1)

            print("Testing 401 behavior...")
            page.unroute("**huggingface.co**") # Remove mock

            def handle_route_401(route):
                if route.request.method == "OPTIONS":
                    route.fulfill(status=200, headers={"Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST", "Access-Control-Allow-Headers": "Authorization, Content-Type"})
                else:
                    route.fulfill(status=401, body='Unauthorized', headers={"Access-Control-Allow-Origin": "*"})

            page.route("**huggingface.co**", handle_route_401)

            page.evaluate("askMistral('Hello', true)")

            token = page.evaluate("localStorage.getItem('HF_TOKEN')")
            if not token:
                print("SUCCESS: Token removed from localStorage after 401.")
            else:
                print(f"FAILURE: Token NOT removed after 401. Found: {token}")
                exit(1)

            print("Testing background trigger (isInteractive=false)...")
            page.evaluate("localStorage.removeItem('HF_TOKEN')")

            dialog_triggered = False
            def unexpected_dialog(dialog):
                nonlocal dialog_triggered
                dialog_triggered = True
                dialog.dismiss()

            page.remove_listener("dialog", handle_dialog)
            page.on("dialog", unexpected_dialog)

            page.evaluate("askMistral('Hello', false)")

            if dialog_triggered:
                print("FAILURE: Background trigger caused a prompt!")
                exit(1)
            else:
                print("SUCCESS: Background trigger did not prompt.")

        except Exception as e:
            print(f"Test Exception: {e}")
            exit(1)

        browser.close()

if __name__ == "__main__":
    verify_byok()

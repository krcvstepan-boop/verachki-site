from playwright.sync_api import sync_playwright
import os

def verify_app():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Capture console logs
        console_logs = []
        page.on("console", lambda msg: console_logs.append(msg))

        # Load the page
        cwd = os.getcwd()
        file_path = f"file://{cwd}/index.html"
        print(f"Loading: {file_path}")
        page.goto(file_path)

        # Wait for page to load
        page.wait_for_load_state("networkidle")

        # Try to call askMistral
        print("Attempting to call askMistral...")
        result = page.evaluate("async () => { try { return await askMistral('test'); } catch(e) { return e.toString(); } }")
        print(f"Result from askMistral: {result}")

        # Take a screenshot
        page.screenshot(path="verification/app_loaded.png")
        print("Screenshot saved to verification/app_loaded.png")

        # Verify console logs for the specific warning
        warnings = [log.text for log in console_logs if log.type == "warning"]
        found_warning = any("AI Token missing" in w for w in warnings)

        if found_warning:
            print("✅ SUCCESS: Found 'AI Token missing' warning in console.")
        else:
            print("❌ FAILURE: Did not find expected warning. Logs:")
            for l in console_logs:
                print(f"[{l.type}] {l.text}")

        # Check for other errors
        errors = [log.text for log in console_logs if log.type == "error"]
        if errors:
            print("🚨 Console Errors found:", errors)

if __name__ == "__main__":
    verify_app()

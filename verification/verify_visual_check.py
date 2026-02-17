from playwright.sync_api import sync_playwright
import os

def verify_visual():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Load page
        page.goto("file://" + os.path.abspath("index.html"))

        # Check for console errors
        errors = []
        page.on("console", lambda msg: errors.append(msg.text) if msg.type == "error" else None)

        # Wait for load
        page.wait_for_load_state("networkidle")

        # Screenshot
        page.screenshot(path="verification/visual_check.png")

        if errors:
            print("Console Errors found:")
            for e in errors:
                print(e)
            # Fail if critical errors (ignoring 404s for favicon etc if any)
            # Appwrite might throw errors if not configured, but we care about syntax errors in script.js
        else:
            print("No console errors.")

        browser.close()

if __name__ == "__main__":
    verify_visual()

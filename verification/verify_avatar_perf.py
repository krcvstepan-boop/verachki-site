from playwright.sync_api import sync_playwright
import os
import sys

def run_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Load index.html
        url = f"file://{os.getcwd()}/index.html"
        print(f"Loading {url}")

        # Abort Appwrite requests to avoid CORS noise
        page.route("**/*appwrite*", lambda route: route.abort())

        page.goto(url)

        # Wait for THREE to be available
        try:
            page.wait_for_function("() => window.THREE !== undefined", timeout=5000)
            print("THREE.js loaded.")
        except Exception as e:
            print("TIMEOUT: THREE.js did not load.")
            # Mock THREE if it fails to load?
            # Assuming it loads because previous run said "THREE.js loaded."
            sys.exit(1)

        # Manually initialize AvatarSystem to bypass auth/UI flow
        print("Initializing AvatarSystem...")
        try:
            page.evaluate("window.AvatarSystem.init()")
        except Exception as e:
            print(f"ERROR initializing AvatarSystem: {e}")
            sys.exit(1)

        # Verify placeholders property exists
        is_defined = page.evaluate("window.AvatarSystem.placeholders !== undefined")
        if not is_defined:
            print("FAILURE: placeholders property is undefined.")
            sys.exit(1)

        # Verify it is an HTMLCollection
        type_name = page.evaluate("Object.prototype.toString.call(window.AvatarSystem.placeholders)")
        print(f"Type of placeholders: {type_name}")
        if "HTMLCollection" not in type_name:
            print("FAILURE: placeholders is not an HTMLCollection.")
            sys.exit(1)

        # Verify liveness
        initial_length = page.evaluate("window.AvatarSystem.placeholders.length")
        print(f"Initial length: {initial_length}")

        # Add a placeholder
        print("Adding a placeholder element...")
        page.evaluate("""
            const el = document.createElement('div');
            el.className = 'soul-avatar-placeholder';
            document.body.appendChild(el);
        """)

        new_length = page.evaluate("window.AvatarSystem.placeholders.length")
        print(f"New length: {new_length}")

        if new_length == initial_length + 1:
            print("SUCCESS: HTMLCollection updated automatically.")
        else:
            print(f"FAILURE: HTMLCollection did not update. Expected {initial_length + 1}, got {new_length}")
            sys.exit(1)

        # Check for console errors during animation
        # We'll collect errors for a few seconds
        errors = []
        def on_console(msg):
            if msg.type == "error":
                text = msg.text
                # Filter out network/CORS errors which are expected in file://
                if "Access to fetch" in text or "Failed to load resource" in text or "net::ERR_FAILED" in text:
                    return
                errors.append(text)

        page.on("console", on_console)

        print("Waiting for animation loop...")
        page.wait_for_timeout(2000)

        if errors:
            print("FAILURE: Console errors detected during animation:")
            for err in errors:
                print(f"- {err}")
            sys.exit(1)
        else:
            print("SUCCESS: No console errors during animation.")

        browser.close()

if __name__ == "__main__":
    run_verification()

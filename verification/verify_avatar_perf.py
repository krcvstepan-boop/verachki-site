from playwright.sync_api import sync_playwright

def verify_avatar_optimization():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        try:
            page.goto("http://localhost:8080/index.html")

            # Call showApp() to initialize AvatarSystem
            page.evaluate("window.showApp()")

            # Wait a bit for initialization
            page.wait_for_timeout(1000)

            # Inject a fake message with placeholder to ensure collection updates (live check)
            page.evaluate("""
                const container = document.getElementById('messages-container');
                const row = document.createElement('div');
                row.className = 'message-row';
                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'TestUser';
                row.appendChild(avatar);
                container.appendChild(row);
            """)

            # Verify
            result = page.evaluate("""
                () => {
                    const sys = window.AvatarSystem;
                    if (!sys) return "No System";
                    if (!sys.placeholders) return "No placeholders";

                    return {
                        isHTMLCollection: sys.placeholders instanceof HTMLCollection,
                        length: sys.placeholders.length
                    };
                }
            """)

            print(f"Result: {result}")

            if isinstance(result, dict) and result['isHTMLCollection'] and result['length'] > 0:
                print("SUCCESS: Optimized live collection is working.")
            else:
                print("FAILURE: Verification failed.")

            page.screenshot(path="verification/avatar_verification.png")

        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="verification/error.png")

        browser.close()

if __name__ == "__main__":
    verify_avatar_optimization()

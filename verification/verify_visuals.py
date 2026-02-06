from playwright.sync_api import sync_playwright
import os
import time

def run_visual_verification():
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        url = f"file://{os.getcwd()}/index.html"
        page.route("**/*appwrite*", lambda route: route.abort())
        page.goto(url)

        # Wait for THREE
        try:
            page.wait_for_function("() => window.THREE !== undefined", timeout=5000)
        except:
            print("THREE.js failed to load")
            # Proceed anyway to see what we get

        # Make app interface visible and remove landing
        page.evaluate("""
            document.getElementById('app-interface').classList.remove('hidden');
            document.querySelector('section.hero').classList.add('hidden');
        """)

        # Initialize AvatarSystem
        page.evaluate("if (window.AvatarSystem) window.AvatarSystem.init()")

        # Add a placeholder in the middle of the screen
        # We need to append it to messages-container ideally, or body, but AvatarSystem checks document.getElementsByClassName
        # It calculates bounding rect relative to viewport, so appending to body is fine for test.
        page.evaluate("""
            const el = document.createElement('div');
            el.className = 'soul-avatar-placeholder';
            el.dataset.user = 'TestUser';
            el.style.position = 'absolute';
            el.style.left = '50%';
            el.style.top = '50%';
            el.style.width = '200px';
            el.style.height = '200px';
            el.style.transform = 'translate(-50%, -50%)';
            el.style.zIndex = '1000';
            // el.style.border = '1px solid red';
            document.body.appendChild(el);
        """)

        # Wait for render
        time.sleep(2)

        # Screenshot
        screenshot_path = "verification/avatar_visual.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run_visual_verification()

import sys
from playwright.sync_api import sync_playwright

def verify_network(page):
    # Intercept Appwrite to prevent actual calls during testing, but allow initial fetch
    # Block external CDNs to speed up
    page.route("**/*.{png,jpg,jpeg,gif,svg}", lambda route: route.abort())
    page.route("https://unpkg.com/**", lambda route: route.abort())

    # Mock ForceGraph3D so we don't need real WebGL just to test the logic
    # Actually, the user's logic is just JS manipulation, so we just run the page
    # But to prevent WebGL errors headlessly, we might just let it run or inject a mock
    # Let's just let it run natively and take a screenshot, it uses ThreeJS.

    page.goto("http://localhost:8080/network.html", wait_until="domcontentloaded")
    page.wait_for_timeout(2000) # Give time for graph to init

    page.screenshot(path="/home/jules/verification/network_optimized.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True, args=['--use-gl=egl']) # Needed for WebGL in headless
        context = browser.new_context(record_video_dir="/home/jules/verification/video")
        page = context.new_page()
        try:
            verify_network(page)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
        finally:
            context.close()
            browser.close()

from playwright.sync_api import sync_playwright
import time

def verify_network_graph():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Block external domains to avoid timeouts
        context = browser.new_context()
        context.route("**/*", lambda route: route.continue_() if "localhost" in route.request.url or "127.0.0.1" in route.request.url or route.request.url.startswith("file://") or "unpkg.com" in route.request.url else route.abort())

        page = context.new_page()

        print("Loading network.html...")
        # Since we already started python3 -m http.server 8080
        page.goto("http://localhost:8080/network.html", wait_until="networkidle")

        print("Waiting for graph to render...")
        # Give the force graph a moment to initialize and settle
        time.sleep(3)

        screenshot_path = "verification/network_graph_optimized.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_network_graph()
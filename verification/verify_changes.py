from playwright.sync_api import sync_playwright

def verify_network_graph():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Block external CDNs and APIs to speed up load and prevent timeouts
        context.route("**/*", lambda route: route.continue_() if "localhost" in route.request.url or "127.0.0.1" in route.request.url or route.request.url.startswith("data:") else route.abort())

        # Read index.html to find out what scripts are actually loaded (ThreeJS, ForceGraph3D)
        # However, blocking them will break the graph. Let's selectively allow unpkg and jsdelivr for ThreeJS/ForceGraph, but maybe we can mock Appwrite?
        # Actually, let's just allow all for a moment, but mock Appwrite DB response so it's fast and doesn't hit external API.

        context_full = browser.new_context()

        # Mock Appwrite API to return dummy users
        def handle_appwrite(route):
            if "cloud.appwrite.io" in route.request.url and "documents" in route.request.url:
                route.fulfill(
                    status=200,
                    content_type="application/json",
                    body='{"documents": [{"username": "user1"}, {"username": "user2"}, {"username": "user3"}, {"username": "user4"}, {"username": "user5"}]}'
                )
            else:
                route.continue_()

        context_full.route("**/*", handle_appwrite)

        page = context_full.new_page()
        page.goto("http://localhost:8080/network.html", wait_until="networkidle", timeout=30000)

        # Wait a bit for the graph to render (ForceGraph3D uses canvas)
        page.wait_for_timeout(3000)

        # Take screenshot
        page.screenshot(path="verification/network_graph.png")

        browser.close()

if __name__ == "__main__":
    verify_network_graph()

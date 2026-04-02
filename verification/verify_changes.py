from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Verify Landing
        print("Checking index.html...")
        page.goto("http://localhost:8080/index.html")
        page.wait_for_timeout(1000) # Wait for potential animations/load
        page.screenshot(path="verification/landing.png")

        # Verify Network
        print("Checking network.html...")
        page.goto("http://localhost:8080/network.html")
        page.wait_for_timeout(1000)

        # Check for translated text
        link = page.get_by_text("НАЗАД В МИР")
        expect(link).to_be_visible()

        page.screenshot(path="verification/network.png")
        print("Verification complete.")
        browser.close()

if __name__ == "__main__":
    run()

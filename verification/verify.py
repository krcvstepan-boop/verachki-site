from playwright.sync_api import sync_playwright

def verify_changes():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Navigate to the page
        page.goto("http://localhost:8080/index.html")

        # 1. Check if Defcon widget is gone
        defcon = page.query_selector(".defcon-widget")
        if defcon:
            print("FAILURE: Defcon widget found!")
        else:
            print("SUCCESS: Defcon widget NOT found.")

        # 2. Check if avatar canvas exists
        canvas = page.query_selector("#soul-avatars")
        if canvas:
            print("SUCCESS: Soul Avatars canvas found.")
        else:
            print("FAILURE: Soul Avatars canvas NOT found.")

        # 3. Check console for errors
        page.on("console", lambda msg: print(f"CONSOLE: {msg.text}"))

        # Wait a bit for JS to run
        page.wait_for_timeout(2000)

        # Screenshot
        page.screenshot(path="verification/verification.png")

        browser.close()

if __name__ == "__main__":
    verify_changes()

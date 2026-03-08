from playwright.sync_api import sync_playwright

def verify_byok_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Override prompt before navigation
        context.add_init_script('''
            window.prompt = function(msg) {
                return "fake_token_123";
            };
        ''')

        page.goto("http://localhost:8080/index.html")

        page.wait_for_timeout(1000)

        # Call askMistral
        page.evaluate('''
            askMistral("Hello AI", true).catch(e => console.error(e));
        ''')

        page.wait_for_timeout(1000)

        hf_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
        print(f"HF_TOKEN in localStorage: {hf_token}")

        page.screenshot(path="verification/sentinel_verification.png")
        context.close()
        browser.close()

if __name__ == "__main__":
    verify_byok_flow()

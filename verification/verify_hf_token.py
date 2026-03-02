from playwright.sync_api import sync_playwright, expect

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()

        # Mock window.prompt
        page.add_init_script("""
            window.prompt = function(msg) {
                console.log("PROMPT CALLED: " + msg);
                return "mock_hf_token_123";
            };
        """)

        # Add mock for askMistral interaction
        page.add_init_script("""
            window.mockTriggerAI = async function() {
                try {
                    // Try direct call which sets isInteractive to true
                    await window.askMistral("test prompt", true);
                    const token = localStorage.getItem('HF_TOKEN');
                    document.body.innerHTML += `<div id="verification-result">Token Saved: ${token}</div>`;
                } catch (e) {
                    console.error(e);
                }
            };
        """)

        print("Checking HF Token BYOK flow...")
        page.goto("http://localhost:8080/index.html")
        page.wait_for_timeout(1000)

        # Execute our mock trigger
        page.evaluate("window.mockTriggerAI()")
        page.wait_for_timeout(1000)

        # Check if token was saved to DOM
        result = page.locator("#verification-result")
        expect(result).to_have_text("Token Saved: mock_hf_token_123")

        page.screenshot(path="verification/hf_token_flow.png")
        print("Verification complete.")
        browser.close()

if __name__ == "__main__":
    run()

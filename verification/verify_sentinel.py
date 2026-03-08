from playwright.sync_api import Page, expect, sync_playwright

def verify_byok_flow(page: Page):
    # Load index.html locally
    page.goto("http://localhost:8080/index.html")

    # Inject auth state to bypass Appwrite
    page.evaluate('''
        state.user = { $id: "test-user", name: "Sentinel", email: "sentinel@test.com" };
        state.profile = { $id: "test-profile", username: "Sentinel", rank: "Элита" };
        updateLandingState(true);
    ''')

    # Show app interface
    page.evaluate("showApp()")

    # Wait for the chat interface to be visible
    expect(page.locator("#app-interface")).to_be_visible()

    # Stub askMistral to return a fake response and check if prompt was called
    # We will override window.prompt to simulate user input
    page.add_init_script('''
        window.promptCalled = false;
        window.prompt = function(msg) {
            window.promptCalled = true;
            return "fake_token_123";
        };
    ''')

    # Since askMistral is bound to the window/global scope we can just call it
    page.evaluate('''
        askMistral("Hello AI", true).catch(e => console.error(e));
    ''')

    # Give it a tiny bit of time to execute the prompt
    page.wait_for_timeout(500)

    # Check if prompt was called and localStorage was updated
    prompt_called = page.evaluate("window.promptCalled")
    hf_token = page.evaluate("localStorage.getItem('HF_TOKEN')")

    print(f"Prompt called: {prompt_called}")
    print(f"HF_TOKEN in localStorage: {hf_token}")

    # Take a screenshot of the chat interface for visual verification
    page.screenshot(path="verification/sentinel_verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()
        try:
            verify_byok_flow(page)
        except Exception as e:
            print(f"Verification failed: {e}")
        finally:
            context.close()
            browser.close()

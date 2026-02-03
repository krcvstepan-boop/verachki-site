from playwright.sync_api import sync_playwright, expect

def test_hf_token_logic(page):
    print("Navigating to page...")
    page.goto("http://localhost:8080/index.html")
    expect(page).to_have_title("VERACHKI | Empire of Silence")

    # 1. Verify localStorage is empty initially
    token = page.evaluate("localStorage.getItem('HF_TOKEN')")
    assert token is None, "Token should be None initially"

    # 2. Handle the prompt by returning a mock token
    def handle_dialog(dialog):
        print(f"Dialog message: {dialog.message}")
        dialog.accept("mock_token_123")

    page.on("dialog", handle_dialog)

    # 3. Call getHFToken() via evaluate. This should trigger the prompt.
    print("Waiting for getHFToken function...")
    page.wait_for_function("typeof window.getHFToken === 'function'")

    print("Calling getHFToken()...")
    result = page.evaluate("window.getHFToken()")

    assert result == "mock_token_123", f"Expected 'mock_token_123', got {result}"

    # 4. Verify it is saved to localStorage
    stored_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
    assert stored_token == "mock_token_123", "Token should be saved to localStorage"

    # 5. Call again, should return stored token without prompt
    result_cached = page.evaluate("window.getHFToken()")
    assert result_cached == "mock_token_123", "Should return cached token"

    print("HF Token Logic Verified!")

    # Screenshot
    page.screenshot(path="/home/jules/verification/verification.png")

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            test_hf_token_logic(page)
        except Exception as e:
            print(f"Test failed: {e}")
            page.screenshot(path="/home/jules/verification/error.png")
            raise e
        finally:
            browser.close()

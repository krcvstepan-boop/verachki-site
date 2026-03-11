from playwright.sync_api import sync_playwright

def verify_script():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Mock prompt to simulate BYOK interaction
        context.add_init_script("""
            window.prompt = function(msg) {
                console.log("Prompt intercepted: " + msg);
                return "fake_hf_token_123";
            };
        """)

        # Intercept HuggingFace API call to verify it uses the fake token
        def handle_route(route, request):
            if "api-inference.huggingface.co" in request.url:
                headers = request.headers
                assert headers.get("authorization") == "Bearer fake_hf_token_123", f"Expected Bearer fake_hf_token_123, got {headers.get('authorization')}"
                route.fulfill(status=200, json=[{"generated_text": "Mocked AI Response"}])
            else:
                route.continue_()

        page.route("**/*", handle_route)

        # We need to bypass appwrite auth to get to the chat interface.
        # But for this test, since the askMistral function is global, we can just call it via evaluate.
        page.goto("http://localhost:8080/index.html")

        # Call askMistral interactively
        result = page.evaluate("""
            async () => {
                return await askMistral("Hello AI", true);
            }
        """)

        print(f"AI Result: {result}")
        assert result == "Mocked AI Response"
        print("BYOK integration verified successfully.")

        browser.close()

if __name__ == "__main__":
    verify_script()

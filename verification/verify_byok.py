from playwright.sync_api import sync_playwright

def run_cuj(page):
    # Mock global variables and Appwrite methods to bypass auth and load UI directly
    page.add_init_script("""
        window.promptText = null;
        window.prompt = function(msg) {
            window.promptText = msg;
            return "hf_mock_token_12345";
        };

        window.state = {
            user: { $id: "user1", name: "TestUser", email: "test@test.com" },
            profile: { $id: "prof1", username: "TestUser", rank: "Имперец", ether: 0, flower_xp: 0 },
            profileCache: new Map(),
            editingId: null,
            isLogin: true,
            currentProfileId: null,
            attachment: null,
            recorder: null,
            chunks: [],
            isRecording: false,
            audioPlayer: null,
            isUploading: false,
            isRadioMode: false,
            radioNoise: null,
            aiCooldown: false,
            claimTimer: null
        };
        window.countdownInterval = null;
        window.countdownAnimFrame = null;

        // Mock Appwrite so we don't throw errors
        window.Appwrite = {
            Client: class { setEndpoint(){return this;} setProject(){return this;} subscribe(){return this;} },
            Account: class { async get(){ return window.state.user; } },
            Databases: class {
                async listDocuments(){ return { documents: [window.state.profile] }; }
                async createDocument(){ return window.state.profile; }
            },
            Storage: class {},
            ID: { unique: () => "id_" + Date.now() },
            Query: { equal: ()=>"", orderAsc: ()=>"", limit: ()=>"" }
        };
        // Mock instantiated client db to bypass fetching
        window.db = new window.Appwrite.Databases();
    """)

    # Mock external HuggingFace API
    def handle_hf_route(route):
        route.fulfill(
            status=200,
            json=[{"generated_text": "Mock AI Response"}],
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Credentials": "true"
            }
        )
    page.route("https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3", handle_hf_route)

    # Mock specific Appwrite network calls to bypass auth issues during load
    page.route("**/v1/account", lambda route: route.fulfill(status=200, json={"$id": "user1", "name": "TestUser", "email": "test@test.com"}))
    page.route("**/v1/databases/*/collections/*/documents*", lambda route: route.fulfill(status=200, json={"documents": [{"$id": "prof1", "username": "TestUser", "rank": "Имперец", "ether": 0, "flower_xp": 0}]}))

    # Abort unneeded real network calls
    page.route("**/v1/realtime*", lambda route: route.abort())

    page.goto("http://localhost:8080")
    page.wait_for_timeout(500)

    # Force show app interface since we bypassed standard login flow
    page.evaluate("""
        document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
        document.getElementById('app-interface').classList.remove('hidden');
    """)
    page.wait_for_timeout(500)

    # Trigger AI direct call
    page.evaluate("tryTriggerAI('ии, привет')")
    page.wait_for_timeout(1000)

    # Verify that the token was added to localStorage after prompt
    hf_token = page.evaluate("localStorage.getItem('HF_TOKEN')")
    assert hf_token == "hf_mock_token_12345", f"Expected token 'hf_mock_token_12345', got {hf_token}"

    # Check that prompt was called
    prompt_msg = page.evaluate("window.promptText")
    assert "Hugging Face" in prompt_msg, "Prompt message did not contain expected text"

    page.screenshot(path="verification/screenshots/byok_verification.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
    import os
    os.makedirs("verification/videos", exist_ok=True)
    os.makedirs("verification/screenshots", exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="verification/videos"
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()

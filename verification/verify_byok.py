import asyncio
import json
import base64
from playwright.sync_api import sync_playwright, expect

def test_byok_flow():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Grant localStorage permissions just in case
        context = browser.new_context(
            permissions=["clipboard-read", "clipboard-write"]
        )
        page = context.new_page()

        # Mock Appwrite and Fetch via init script to bypass auth and external calls
        page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                },
                Account: class {
                    async get() { return { $id: 'test-user', name: 'Test User', email: 'test@example.com' }; }
                    async createEmailPasswordSession() { return {}; }
                    async deleteSession() { return {}; }
                },
                Databases: class {
                    async listDocuments() { return { documents: [] }; }
                    async createDocument(dbId, colId, docId, data) {
                        // Simulate receiving a message
                        setTimeout(() => {
                            if (window.handleRealtimeEvent) {
                                window.handleRealtimeEvent({
                                    events: ['databases.*.collections.*.documents.*.create'],
                                    payload: { $id: docId, ...data }
                                });
                            }
                        }, 100);
                        return { $id: docId, ...data };
                    }
                },
                Storage: class {
                    getFileView() { return { href: 'mock-url' }; }
                },
                ID: { unique: () => 'id-' + Math.random().toString(36).substr(2, 9) },
                Query: {
                    orderAsc: () => 'orderAsc',
                    orderDesc: () => 'orderDesc',
                    limit: () => 'limit',
                    equal: () => 'equal',
                    select: () => 'select'
                }
            };

            // Override window.prompt to return our mock token
            window.prompt = function(message) {
                console.log('Prompt triggered with message:', message);
                return 'mock_hf_token_123';
            };

            // Mock fetch to intercept HuggingFace API calls
            const originalFetch = window.fetch;
            window.fetch = async function(resource, options) {
                let url = '';
                let headers = {};
                if (resource instanceof Request) {
                    url = resource.url;
                    headers = Object.fromEntries(resource.headers.entries());
                } else {
                    url = resource;
                    headers = options?.headers || {};
                }

                if (url.includes('huggingface.co')) {
                    console.log('HF API called with headers:', headers);
                    // Verify the Authorization header contains our mocked token
                    if (headers['Authorization'] === 'Bearer mock_hf_token_123' || headers['authorization'] === 'Bearer mock_hf_token_123') {
                        return {
                            ok: true,
                            status: 200,
                            json: async () => [{ generated_text: "Mocked AI response via BYOK!" }]
                        };
                    } else {
                        return {
                            ok: false,
                            status: 401,
                            json: async () => ({ error: "Unauthorized" })
                        };
                    }
                }

                // Block other external requests to prevent hanging
                if (!url.startsWith('http://localhost') && !url.startsWith('file://')) {
                    return { ok: true, status: 200, json: async () => ({}) };
                }

                return originalFetch(resource, options);
            };
        """)

        # Block external resources except localhost to speed up loading and prevent CORS/timeouts
        page.route("**/*", lambda route: route.continue_() if "localhost" in route.request.url or "127.0.0.1" in route.request.url or route.request.url.startswith("file://") or route.request.url.startswith("data:") else route.fulfill(status=200, body=""))

        # Navigate to the local server
        page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

        # Explicitly initialize the state and bypass the login screen
        page.evaluate("""
            window.state.user = { $id: 'test-user', name: 'Test User', email: 'test@example.com' };
            window.state.profile = { flower_xp: 0, ether: 0, rank: 'Test' };
            window.state.aiCooldown = false;
            // Define handleRealtimeEvent globally for the mock DB to use
            window.handleRealtimeEvent = function(data) {
                const ev = data.events[0];
                const payload = data.payload;
                if(ev.includes('.create')) {
                    const messagesContainer = document.getElementById('messages-container');
                    const div = document.createElement('div');
                    div.className = 'message ai-message';
                    div.innerHTML = `<div class="msg-content"><div class="msg-sender">${payload.senderId}</div><div class="msg-text"><span class="msg-text-content">${payload.messageContent}</span></div></div>`;
                    messagesContainer.appendChild(div);
                }
            };
            document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
            document.getElementById('app-interface').classList.remove('hidden');
        """)

        # Clear localStorage to ensure prompt is triggered
        page.evaluate("localStorage.removeItem('HF_TOKEN');")

        # Wait for the chat interface to be visible
        expect(page.locator("#app-interface")).to_be_visible()

        # Override state.profile just in case the app overwrites it during load
        page.evaluate("window.state.profile = { username: 'testuser', flower_xp: 0, ether: 0, rank: 'Test' }; window.state.user = { $id: 'test-user', name: 'Test User', email: 'test@example.com' };")

        # Type a direct message to trigger the AI
        chat_input = page.locator("#msg-input")
        chat_input.fill("Система, привет!")

        # Click send
        send_btn = page.locator("#send-btn")
        send_btn.click()

        # Call tryTriggerAI manually to bypass any UI/DB logic complexities that may not be mocked perfectly
        page.evaluate("window.tryTriggerAI('Система, привет!')")

        # Wait for the AI's mocked response to appear in the chat
        ai_message = page.locator(".ai-message .msg-text-content").filter(has_text="Mocked AI response via BYOK!")
        expect(ai_message).to_be_visible(timeout=5000)

        # Verify that the token was saved to localStorage
        token_in_storage = page.evaluate("localStorage.getItem('HF_TOKEN')")
        assert token_in_storage == 'mock_hf_token_123', f"Expected token 'mock_hf_token_123' in localStorage, but got {token_in_storage}"

        # Take a screenshot to verify the AI message appeared
        page.screenshot(path="verification/byok_verification.png")
        print("BYOK flow test passed! Screenshot saved to verification/byok_verification.png")

        browser.close()

if __name__ == "__main__":
    test_byok_flow()

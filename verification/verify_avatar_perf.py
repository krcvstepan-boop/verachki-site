import sys
from playwright.sync_api import sync_playwright

def verify():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            viewport={'width': 1280, 'height': 800},
            record_video_dir="verification/video"
        )

        # Block external CDNs that might cause timeouts
        context.route('**/*.{png,jpg,jpeg,gif,svg,woff2}', lambda route: route.abort())
        context.route('https://unpkg.com/**', lambda route: route.abort())
        context.route('https://cdn.jsdelivr.net/**', lambda route: route.abort())
        context.route('https://cloud.appwrite.io/**', lambda route: route.abort())

        page = context.new_page()

        page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                    subscribe() { return this; }
                },
                Account: class {
                    get() { return Promise.resolve({ $id: 'test-user', name: 'Test User' }); }
                    createAnonymousSession() { return Promise.resolve({}); }
                },
                Databases: class {
                    listDocuments() { return Promise.resolve({ documents: [] }); }
                    createDocument() { return Promise.resolve({}); }
                }
            };
            window.state = {
                user: { $id: 'test-user', name: 'Test User' },
                profile: { username: 'test-user', flower_xp: 50 },
                aiCooldown: false
            };
        """)

        print("Navigating to index.html...")
        page.goto("http://localhost:8080/index.html", wait_until="networkidle")
        page.wait_for_timeout(1000)

        # Login to app natively using the standard flow by firing the custom event
        page.evaluate("""
            const evt = new CustomEvent('auth-success');
            window.dispatchEvent(evt);
        """)

        page.wait_for_timeout(1000)

        page.evaluate("""
            if (typeof addMessage === 'function') {
                for (let i = 0; i < 5; i++) {
                    addMessage(`Test message ${i}`, `ai-user-${i}`, false, 50);
                }
            } else {
                console.log("addMessage function not found");
            }
        """)

        page.wait_for_timeout(2000)

        visible_count = page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Number of visible avatars tracked: {visible_count}")

        page.screenshot(path="verification/avatar_perf.png")
        print("Screenshot saved to verification/avatar_perf.png")

        context.close()
        browser.close()

if __name__ == "__main__":
    verify()

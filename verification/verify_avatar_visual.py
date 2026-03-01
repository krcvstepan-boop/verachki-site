import time
from playwright.sync_api import sync_playwright

def verify_avatar_visual():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Inject mocks for Appwrite to prevent network hang
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } },
                Account: class { get() { return Promise.reject(); } createEmailPasswordSession() {} create() {} deleteSession() {} },
                Databases: class { listDocuments() { return Promise.resolve({documents: []}); } createDocument() {} updateDocument() {} deleteDocument() {} },
                Storage: class { createFile() {} getFileView() {} },
                ID: { unique: () => 'test-id' },
                Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
            };
            window.fetch = () => Promise.resolve({ ok: true, json: () => Promise.resolve([]) });
        """)

        # Navigate to local server
        page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

        # Show App interface directly
        page.evaluate("showApp()")

        # Ensure avatar system initializes
        page.evaluate("if (window.AvatarSystem) { window.AvatarSystem.init(); }")

        # Wait for interface to appear
        page.wait_for_selector("#app-interface", state="visible")

        # Inject some fake messages with avatars to test the new loop
        page.evaluate("""
            const container = document.getElementById('messages-container');
            container.innerHTML = '';

            for(let i=0; i<3; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'user' + i;
                row.appendChild(avatar);

                const msg = document.createElement('div');
                msg.className = 'message';
                msg.innerHTML = '<div class="msg-text"><span class="msg-text-content">Test message ' + i + '</span></div>';
                row.appendChild(msg);

                container.appendChild(row);
            }
        """)

        # Give it a moment to render avatars
        time.sleep(2)

        # Take a screenshot to verify avatars are visible
        page.screenshot(path="verification/avatar_optimization_visual.png")
        print("Screenshot saved to verification/avatar_optimization_visual.png")

        # Verify visibility set
        visible_count = page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible avatars tracked: {visible_count}")

        browser.close()

if __name__ == "__main__":
    verify_avatar_visual()

from playwright.sync_api import sync_playwright
import os
import sys

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        file_path = os.path.abspath("index.html")
        url = f"file://{file_path}"

        # Inject Mock
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() { return { unsubscribe: () => {} }; } },
                Account: class { get() { return Promise.reject("Mock Error"); } },
                Databases: class { listDocuments() { return Promise.resolve({documents: []}); } createDocument() { return Promise.resolve({}); } },
                Storage: class {},
                ID: { unique: () => 'id' },
                Query: { equal: () => '', orderAsc: () => '', limit: () => '' }
            };
        """)

        page.goto(url)
        page.wait_for_load_state("networkidle")

        # Init AvatarSystem & Messages
        page.evaluate("""
            const app = document.getElementById('app-interface');
            app.classList.remove('hidden');
            const container = document.getElementById('messages-container');
            container.innerHTML = '';

            if (window.AvatarSystem) {
                // Use REAL WebGLRenderer if available, otherwise mock drawing 2D rectangles on canvas
                // Playwright headless usually supports WebGL.
                // We'll trust it works.
                window.AvatarSystem.init();
            }

            // Add messages
            for(let i=0; i<10; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                row.style.height = '100px';
                row.style.marginBottom = '20px';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'user' + i;
                avatar.style.width = '50px';
                avatar.style.height = '50px';
                // Force background so we see placeholder even if 3D fails
                avatar.style.background = 'rgba(0,0,0,0.1)';

                row.appendChild(avatar);
                container.appendChild(row);
            }
        """)

        page.wait_for_timeout(2000)

        # Take screenshot
        screenshot_path = "verification/visual_check.png"
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        # Verify visible avatars count logic again just in case
        count = page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible Avatars: {count}")

        if count == 0:
            print("FAILURE: No visible avatars detected.")
            sys.exit(1)

        browser.close()

if __name__ == "__main__":
    run()

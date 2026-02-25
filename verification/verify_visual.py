from playwright.sync_api import sync_playwright
import os
import time

def verify_visual():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Mock Appwrite and other externals to avoid errors
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint(){ return this; } setProject(){ return this; } subscribe(){ return {}; } },
                Account: class { get() { return Promise.reject(); } createEmailPasswordSession() { return Promise.resolve(); } },
                Databases: class { listDocuments() { return Promise.resolve({documents: []}); } createDocument() { return Promise.resolve({}); } },
                Storage: class { getFileView() { return ''; } },
                ID: { unique: () => 'id-' + Math.random() },
                Query: { orderAsc: () => {}, limit: () => {}, equal: () => {} }
            };
        """)

        # Load index.html
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Wait for load
        page.wait_for_load_state("domcontentloaded")

        # Inject messages to trigger avatar creation
        page.evaluate("""
            const container = document.getElementById('messages-container');
            // Show app interface
            document.getElementById('app-interface').classList.remove('hidden');
            document.getElementById('soul-avatars').style.display = 'block';

            // Init Avatar System
            if (window.AvatarSystem) {
                window.AvatarSystem.init();
            }

            // Create fake messages with avatars
            for(let i=0; i<5; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'User' + i;
                avatar.style.width = '50px';
                avatar.style.height = '50px';
                avatar.style.background = 'rgba(0,0,0,0.1)'; // Visual debug
                row.appendChild(avatar);

                const msg = document.createElement('div');
                msg.className = 'message';
                msg.innerText = 'Hello ' + i;
                row.appendChild(msg);

                container.appendChild(row);
            }
        """)

        # Wait for canvas to render (give it some time for RAF loops)
        time.sleep(2)

        # Screenshot
        screenshot_path = os.path.join(cwd, "verification/visual_check.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    verify_visual()

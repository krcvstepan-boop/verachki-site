from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Mock Appwrite
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() {} },
                Account: class { get() { return Promise.reject(); } },
                Databases: class { listDocuments() { return Promise.resolve({documents: []}); } },
                Storage: class {},
                ID: { unique: () => 'id' },
                Query: { orderAsc: () => {}, limit: () => {}, equal: () => {} }
            };
        """)

        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Wait for AvatarSystem
        page.wait_for_function("() => window.AvatarSystem")
        page.evaluate("window.AvatarSystem.init()")

        # Show app
        page.evaluate("document.getElementById('app-interface').classList.remove('hidden')")

        # Inject avatars
        page.evaluate("""
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            for(let i=0; i<5; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'user' + i;
                avatar.style.width = '40px';
                avatar.style.height = '40px';
                avatar.style.marginRight = '10px';

                const msg = document.createElement('div');
                msg.className = 'message';
                msg.innerText = 'Message ' + i;

                row.appendChild(avatar);
                row.appendChild(msg);
                container.appendChild(row);
            }
        """)

        # Wait for render
        page.wait_for_timeout(2000)

        # Screenshot
        page.screenshot(path="verification/visual_check.png")
        print("Screenshot saved to verification/visual_check.png")

        browser.close()

if __name__ == "__main__":
    run()

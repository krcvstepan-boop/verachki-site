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

        # Init AvatarSystem
        page.wait_for_function("() => window.AvatarSystem")
        page.evaluate("window.AvatarSystem.init()")

        # Inject some avatars to visualize
        page.evaluate("""
            document.getElementById('app-interface').classList.remove('hidden');
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            for(let i=0; i<5; i++) {
                const div = document.createElement('div');
                div.className = 'soul-avatar-placeholder';
                div.style.height = '100px';
                div.style.width = '100px';
                div.style.margin = '20px';
                div.style.border = '1px solid #ccc';
                div.dataset.user = 'user' + i;
                container.appendChild(div);
            }
        """)

        # Wait for rendering
        page.wait_for_timeout(2000)

        # Screenshot
        page.screenshot(path="verification/visual_check.png")
        print("Screenshot saved to verification/visual_check.png")

        browser.close()

if __name__ == "__main__":
    run()

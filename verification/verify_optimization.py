from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Mock Appwrite to prevent script.js errors blocking execution
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

        # Load file
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Wait for AvatarSystem
        page.wait_for_function("() => window.AvatarSystem")

        # Init AvatarSystem manually if not initialized (force it for test)
        page.evaluate("window.AvatarSystem.init()")

        # Inject some avatars
        # We inject them into messages-container which is hidden by default (#app-interface is hidden)
        # We need to show #app-interface to make IntersectionObserver work (elements must be rendered)
        page.evaluate("""
            document.getElementById('app-interface').classList.remove('hidden');
            const container = document.getElementById('messages-container');
            container.innerHTML = ''; // Clear existing
            for(let i=0; i<50; i++) {
                const div = document.createElement('div');
                div.className = 'soul-avatar-placeholder';
                div.style.height = '50px';
                div.style.width = '50px';
                div.style.marginBottom = '50px'; // Spacing
                div.style.border = '1px solid red';
                div.dataset.user = 'user' + i;
                container.appendChild(div);
            }
        """)

        # Wait for IntersectionObserver to trigger
        page.wait_for_timeout(1000)

        # Check visibleAvatars size
        visible_avatars_defined = page.evaluate("window.AvatarSystem.visibleAvatars !== undefined")

        if not visible_avatars_defined:
            print("Before Optimization: visibleAvatars not defined")
        else:
            count = page.evaluate("window.AvatarSystem.visibleAvatars.size")
            print(f"Visible Avatars: {count}")

            # Scroll to bottom
            page.evaluate("document.getElementById('messages-container').scrollTop = 10000")
            page.wait_for_timeout(1000)

            count_after = page.evaluate("window.AvatarSystem.visibleAvatars.size")
            print(f"Visible Avatars after scroll: {count_after}")

        browser.close()

if __name__ == "__main__":
    run()

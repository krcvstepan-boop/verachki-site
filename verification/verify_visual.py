
import os
from playwright.sync_api import sync_playwright

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()

        # Mock Appwrite
        context.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() {} },
                Account: class { get() { return Promise.reject(); } },
                Databases: class { listDocuments() { return Promise.resolve({documents: []}); } },
                Storage: class {},
                ID: { unique: () => 'id-' + Math.random() },
                Query: { orderAsc: () => {}, limit: () => {}, equal: () => {} }
            };
        """)

        page = context.new_page()

        # Load local file
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Wait for load
        page.wait_for_load_state("networkidle")

        # Click "Enter Chat" (mock login by injecting state)
        page.evaluate("""
            window.state.user = { $id: 'u1', name: 'Tester', email: 'test@test.com' };
            window.state.profile = { $id: 'p1', username: 'Tester', rank: 'Imperi', ether: 10, flower_xp: 50 };
            showApp();
        """)

        # Inject a message with avatar
        page.evaluate("""
            const msg = {
                $id: 'msg1',
                messageContent: 'Hello World',
                senderId: 'Tester',
                timestamp: new Date().toISOString(),
                isEdited: false
            };
            renderMessage(msg);
        """)

        # Wait for avatar to render
        page.wait_for_timeout(2000)

        # Screenshot
        os.makedirs("verification", exist_ok=True)
        screenshot_path = os.path.join(cwd, "verification/visual_check.png")
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()

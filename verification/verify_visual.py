from playwright.sync_api import sync_playwright

def run_cuj(page):
    # Mock window.prompt and avoid fetching actual external CDNs blocking render
    page.add_init_script("""
        window.prompt = () => 'mock_token';
        window.state = {
            user: { $id: 'user123', name: 'TestUser', email: 'test@example.com' },
            profile: { $id: 'prof123', username: 'TestUser', rank: 'Наблюдатель', flower_xp: 50, ether: 5 },
            profileCache: new Map(),
            aiCooldown: false
        };
        // Ensure Three.js and AvatarSystem don't crash if loading out of order
        window.addEventListener('load', () => {
             if (window.AvatarSystem) {
                 window.AvatarSystem.init();
                 // Add some mock placeholders so the animate loop has something to process
                 const container = document.getElementById('messages-container');
                 if (container) {
                     for(let i=0; i<3; i++) {
                         const ph = document.createElement('div');
                         ph.className = 'soul-avatar-placeholder';
                         ph.dataset.user = 'user' + i;
                         ph.style.width = '50px';
                         ph.style.height = '50px';
                         container.appendChild(ph);
                     }
                 }
             }
        });
    """)

    # Mock Appwrite API to avoid auth hang
    page.route('**/v1/account*', lambda route: route.fulfill(status=200, json={"$id": "user123", "name": "TestUser", "email": "test@example.com"}))
    page.route('**/v1/databases/*/collections/*/documents*', lambda route: route.fulfill(status=200, json={"documents": [{"$id": "msg1", "senderId": "TestUser", "messageContent": "Hello World", "timestamp": "2023-01-01T00:00:00.000Z"}]}))
    page.route('**/v1/realtime*', lambda route: route.abort())

    # Do NOT block unpkg/jsdelivr as Three.js is loaded from there in index.html

    page.goto("http://localhost:8080/index.html")
    page.wait_for_timeout(1000)

    # Bypass landing page to enter app
    page.evaluate("""
        document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
        document.getElementById('app-interface').classList.remove('hidden');
        if (window.AvatarSystem && !window.AvatarSystem.isRunning) {
            window.AvatarSystem.init();
        }
    """)

    page.wait_for_timeout(2000) # wait for avatars to render

    # Take screenshot
    page.screenshot(path="verification/screenshots/verification.png")
    page.wait_for_timeout(1000)

if __name__ == "__main__":
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

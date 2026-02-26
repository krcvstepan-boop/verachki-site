from playwright.sync_api import sync_playwright
import os

def run_visual_verification():
    with sync_playwright() as p:
        # Launch browser
        browser = p.chromium.launch(headless=True, args=['--no-sandbox', '--disable-setuid-sandbox'])
        page = browser.new_page(viewport={'width': 1280, 'height': 720})

        # Pre-inject mocks BEFORE any script loads
        page.add_init_script("""
            // Mock Appwrite SDK globally
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                    subscribe() {}
                },
                Account: class {
                    get() { return Promise.resolve({ name: 'TestUser', email: 'test@example.com' }); }
                },
                Databases: class {
                    listDocuments() { return Promise.resolve({ documents: [] }); }
                    createDocument() { return Promise.resolve({}); }
                    updateDocument() { return Promise.resolve({}); }
                    deleteDocument() { return Promise.resolve({}); }
                },
                Storage: class {
                    getFileView() { return ''; }
                },
                ID: { unique: () => 'unique_id' },
                Query: { orderAsc: () => {}, limit: () => {}, equal: () => {} }
            };
        """)

        # Load local file
        file_path = os.path.abspath("index.html")
        print(f"Loading: file://{file_path}")
        page.goto(f"file://{file_path}", wait_until="domcontentloaded")

        # Inject content and initialize
        page.evaluate("""
            // 1. Show Interface
            document.getElementById('app-interface').classList.remove('hidden');
            document.getElementById('app-interface').style.display = 'block';

            // 2. Clear and Populate Container
            const container = document.getElementById('messages-container');
            container.innerHTML = '';

            for(let i=0; i<3; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                row.style.display = 'block';
                row.style.marginBottom = '20px';

                const el = document.createElement('div');
                el.className = 'soul-avatar-placeholder';
                el.dataset.user = 'User' + i;

                // Style to ensure visibility for IntersectionObserver
                el.style.width = '50px';
                el.style.height = '50px';
                el.style.background = 'rgba(255, 0, 0, 0.2)';
                el.style.border = '2px solid red';
                el.style.display = 'inline-block';

                row.appendChild(el);
                container.appendChild(row);
            }

            // 3. Init System
            if (window.AvatarSystem) {
                if (!window.AvatarSystem.isRunning) {
                    window.AvatarSystem.init();
                } else {
                    // If already running (from page load), manually trigger scan just in case
                    window.AvatarSystem.setupObservers();
                }
            }
        """)

        # Wait for observers to fire
        page.wait_for_timeout(2000)

        # Check internal state
        result = page.evaluate("""
            (() => {
                const sys = window.AvatarSystem;
                if (!sys) return { error: "System not found" };
                return {
                    visibleCount: sys.visibleAvatars ? sys.visibleAvatars.size : -1,
                    isRunning: sys.isRunning
                };
            })()
        """)

        print(f"Result: {result}")

        # Screenshot
        screenshot_path = "verification/avatar_verification.png"
        page.screenshot(path=screenshot_path, full_page=True)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run_visual_verification()

from playwright.sync_api import sync_playwright, expect
import os
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Record video as instructed by memory
        context = browser.new_context(record_video_dir="verification/videos")
        page = context.new_page()

        try:
            # Mock the state and bypass auth as instructed in memory
            page.add_init_script("""
                window.prompt = () => 'mocked-token';
                window.state = {
                    user: { $id: 'mock-user-id', name: 'TestUser', email: 'test@example.com' },
                    profile: {
                        $id: 'mock-profile-id',
                        username: 'TestUser',
                        flower_xp: 50,
                        ether: 5,
                        rank: 'Наблюдатель'
                    },
                    profileCache: new Map(),
                    aiCooldown: false,
                    isLogin: true
                };
                window.countdownInterval = null;

                // Mock Appwrite so the frontend can initialize
                window.Appwrite = {
                    Client: class {
                        setEndpoint() { return this; }
                        setProject() { return this; }
                        subscribe() { return this; }
                    },
                    Databases: class {
                        listDocuments() {
                            return Promise.resolve({ documents: [] });
                        }
                        createDocument() {
                            return Promise.resolve({
                                $id: 'mock-doc-id',
                                messageContent: 'Test Message',
                                senderId: 'TestUser',
                                timestamp: new Date().toISOString()
                            });
                        }
                    },
                    Account: class {
                        get() {
                            return Promise.resolve(window.state.user);
                        }
                    },
                    Storage: class {},
                    ID: {
                        unique: () => 'unique-id'
                    },
                    Query: {
                        limit: () => {},
                        equal: () => {},
                        orderAsc: () => {}
                    }
                };
            """)

            # Abort Appwrite realtime connection as instructed
            page.route('**/v1/realtime*', lambda route: route.abort())

            # Start server if needed in the background, or just use file path
            # Using HTTP since file:// can cause CORS/module loading issues with Three.js sometimes
            page.goto("http://localhost:8080/index.html", wait_until="domcontentloaded")

            # Let the page load and execute scripts
            page.wait_for_timeout(2000)

            # Trigger the app to show the interface
            page.evaluate("""
                document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
                document.querySelector('footer').style.display = 'none';
                document.querySelector('nav').style.display = 'none';
                document.getElementById('app-interface').classList.remove('hidden');

                // Inject a placeholder to ensure the animate loop runs
                const container = document.getElementById('messages-container');
                const placeholder = document.createElement('div');
                placeholder.className = 'soul-avatar-placeholder';
                placeholder.dataset.user = 'TestUser';
                placeholder.style.width = '50px';
                placeholder.style.height = '50px';
                placeholder.style.position = 'absolute';
                placeholder.style.top = '100px';
                placeholder.style.left = '10px';
                container.appendChild(placeholder);

                if (window.AvatarSystem) {
                    window.AvatarSystem.init();
                    window.AvatarSystem.updateAvatar('TestUser', 50);
                }
            """)

            page.wait_for_timeout(2000)

            # Look for the canvas to ensure it loaded
            canvas = page.locator('canvas#soul-avatars')
            expect(canvas).to_be_visible(timeout=5000)

            # Take a screenshot
            screenshot_path = "verification/screenshots/avatar_optimized.png"
            page.screenshot(path=screenshot_path)
            print(f"Screenshot saved to {screenshot_path}")

        except Exception as e:
            print(f"Error during verification: {e}")
        finally:
            context.close()
            browser.close()

if __name__ == "__main__":
    run()

from playwright.sync_api import sync_playwright
import time

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    context = browser.new_context()

    # Mock Appwrite
    context.add_init_script("""
        window.Appwrite = {
            Client: class {
                setEndpoint() { return this; }
                setProject() { return this; }
            },
            Account: class {
                createEmailSession() { return Promise.resolve({}); }
                get() { return Promise.resolve({$id: 'test', name: 'Tester', prefs: {xp: 50}}); }
            },
            Databases: class {
                listDocuments() { return Promise.resolve({documents: []}); }
            }
        };
    """)

    # Block CDN Appwrite to ensure mock is used
    context.route("**/*appwrite*", lambda route: route.abort())

    page = context.new_page()
    page.goto("http://localhost:8080")

    # Wait for page load
    page.wait_for_load_state("networkidle")

    # Execute script to verify AvatarSystem availability and render
    # We will use the profile canvas to visualize the "Lotus"

    # Make the profile modal visible manually for screenshot
    page.evaluate("""
        const modal = document.getElementById('profile-modal');
        modal.style.display = 'flex';
        modal.style.opacity = '1';

        const canvas = document.getElementById('profile-flower-canvas');
        // Force size
        canvas.width = 300;
        canvas.height = 300;

        // Render a high level avatar (Lotus)
        if (window.AvatarSystem) {
            AvatarSystem.renderProfileAvatar(canvas, 'VisualCheckUser', 60);
        } else {
            console.error("AvatarSystem not found");
        }
    """)

    # Wait for animation to settle/render a few frames
    time.sleep(2)

    # Screenshot the modal
    page.locator("#profile-modal").screenshot(path="verification/avatar_lotus.png")

    # Also screenshot a "Seed" (Level 0)
    page.evaluate("""
        const canvas = document.getElementById('profile-flower-canvas');
        if (window.AvatarSystem) {
            AvatarSystem.renderProfileAvatar(canvas, 'SeedUser', 5);
        }
    """)
    time.sleep(1)
    page.locator("#profile-modal").screenshot(path="verification/avatar_seed.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)

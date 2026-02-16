from playwright.sync_api import sync_playwright
import os
import time

def verify_optimization():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        # Create a new context to inject scripts
        context = browser.new_context()
        page = context.new_page()

        # Get absolute path to index.html
        cwd = os.getcwd()
        file_url = f"file://{cwd}/index.html"

        # Mock Appwrite to prevent errors and verify IO without network dependency
        page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint(){ return this; } setProject(){ return this; } subscribe(){ return { unsubscribe: ()=>{} }; } },
                Account: class { get(){ return Promise.resolve({ $id: 'test', name: 'Tester', email: 'test@example.com' }); } createEmailPasswordSession(){ return Promise.resolve({}); } },
                Databases: class {
                    listDocuments(){ return Promise.resolve({ documents: [] }); }
                    createDocument(){ return Promise.resolve({}); }
                    updateDocument(){ return Promise.resolve({}); }
                    deleteDocument(){ return Promise.resolve({}); }
                },
                Storage: class { getFileView(){ return ''; } },
                ID: { unique: () => 'id-' + Math.random() },
                Query: { equal: () => {}, limit: () => {}, orderAsc: () => {} }
            };
            // Mock THREE to avoid WebGL context errors in headless (optional but safer)
            // Actually we need THREE to be real for AvatarSystem to work?
            // AvatarSystem checks window.THREE.
            // Let's rely on the real THREE.js loading from CDN.
            // But we might need to wait for it.
        """)

        # Navigate to the page
        print(f"Loading {file_url}...")
        page.goto(file_url)

        # Wait for AvatarSystem to be ready
        page.wait_for_function("() => window.AvatarSystem && window.AvatarSystem.init")

        # Manually trigger init if not triggered (usually triggered by showApp)
        # We can simulate showApp
        page.evaluate("window.showApp()")

        # Wait a bit for init to complete
        page.wait_for_timeout(1000)

        # Inject Dummy Messages with placeholders
        # Create 50 messages. Some should be visible, some not.
        print("Injecting 50 dummy messages...")
        page.evaluate("""
            const container = document.getElementById('messages-container');
            container.innerHTML = ''; // Clear existing

            for(let i=0; i<50; i++) {
                const div = document.createElement('div');
                div.className = 'message-row';
                div.style.height = '100px'; // Ensure height so they take space
                div.style.marginBottom = '20px';
                div.innerHTML = `
                    <div class="soul-avatar-placeholder" data-user="User${i}" style="width:50px; height:50px; background:red;"></div>
                    <div class="message">Message ${i}</div>
                `;
                container.appendChild(div);
            }
        """)

        # Wait for MutationObserver / IntersectionObserver to process
        page.wait_for_timeout(2000)

        # Verify visibleAvatars set size
        # With 100px height + 20px margin = 120px per item.
        # Window height is typically 600-800px in headless.
        # So maybe 5-8 items should be visible + margin.

        visible_count = page.evaluate("window.AvatarSystem.visibleAvatars ? window.AvatarSystem.visibleAvatars.size : -1")
        print(f"Visible Avatars Count: {visible_count}")

        if visible_count == -1:
            print("FAILURE: visibleAvatars Set not found (Optimization not applied).")
            # This is expected before optimization
        elif visible_count == 0:
             print("WARNING: visibleAvatars is 0. Might be an issue with Observer or layout.")
        elif visible_count > 0 and visible_count < 50:
            print(f"SUCCESS: visibleAvatars has {visible_count} items (Subset of 50). Optimization likely working.")
        elif visible_count == 50:
            print("WARNING: All 50 avatars are visible? Screen might be huge or IO not filtering.")

        # Scroll to bottom
        print("Scrolling to bottom...")
        page.evaluate("document.getElementById('messages-container').scrollTop = document.getElementById('messages-container').scrollHeight")
        page.wait_for_timeout(1000)

        new_visible_count = page.evaluate("window.AvatarSystem.visibleAvatars ? window.AvatarSystem.visibleAvatars.size : -1")
        print(f"New Visible Avatars Count after scroll: {new_visible_count}")

        browser.close()

if __name__ == "__main__":
    verify_optimization()

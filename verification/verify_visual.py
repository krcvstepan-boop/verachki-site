from playwright.sync_api import sync_playwright
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # Mock Appwrite globally before scripts load
        page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint(){ return this; }
                    setProject(){ return this; }
                    subscribe(){ return { unsubscribe: ()=>{} }; }
                },
                Account: class {
                    get(){ return Promise.resolve({name:'TestUser', email:'test@test.com', $id:'123'}); }
                    createEmailPasswordSession(){ return Promise.resolve({}); }
                    create(){ return Promise.resolve({}); }
                    deleteSession(){ return Promise.resolve({}); }
                },
                Databases: class {
                    listDocuments(){ return Promise.resolve({documents:[]}); }
                    createDocument(){ return Promise.resolve({}); }
                    updateDocument(){ return Promise.resolve({}); }
                    deleteDocument(){ return Promise.resolve({}); }
                },
                Storage: class {
                    createFile(){ return Promise.resolve({$id:'file123'}); }
                    getFileView(){ return 'placeholder.jpg'; }
                },
                ID: { unique: () => 'unique_' + Math.random() },
                Query: {
                    orderAsc:()=>{}, limit:()=>{}, equal:()=>{}
                }
            };
        """)

        # Block external Appwrite script to ensure mock is used
        page.route("**/*appwrite*", lambda route: route.abort())

        # Load index.html locally
        cwd = os.getcwd()
        page.goto(f"file://{cwd}/index.html")

        # Inject CSS to force visibility of chat interface for screenshot
        page.add_style_tag(content="""
            #app-interface { display: block !important; opacity: 1 !important; visibility: visible !important; }
            section { display: none !important; }
            #messages-container {
                overflow: auto;
                height: 100vh;
                background: #f0f0f0;
                position: relative;
                z-index: 100;
            }
            .soul-avatar-placeholder {
                width: 50px;
                height: 50px;
                background: rgba(255,0,0,0.2); /* Semi-transparent red to see if 3D overlay works */
                border: 1px solid red;
                display: inline-block;
            }
        """)

        # Wait for Three.js to load (it might take a moment if from CDN)
        # If CDN fails, we might need to mock THREE too, but let's hope it works.
        page.wait_for_timeout(3000)

        # Inject a message with avatar placeholder
        page.evaluate("""
            const container = document.getElementById('messages-container');
            container.innerHTML = ''; // Clear loading message

            const row = document.createElement('div');
            row.className = 'message-row';
            row.style.height = '100px';
            row.style.marginBottom = '20px';
            row.style.display = 'flex';
            row.style.alignItems = 'center';
            row.style.padding = '10px';

            const avatar = document.createElement('div');
            avatar.className = 'soul-avatar-placeholder';
            avatar.dataset.user = 'VisualTestUser';

            row.appendChild(avatar);

            const msg = document.createElement('div');
            msg.className = 'message';
            msg.innerText = 'Visual Verification Message';
            msg.style.marginLeft = '10px';
            msg.style.padding = '10px';
            msg.style.background = '#fff';
            msg.style.borderRadius = '8px';
            row.appendChild(msg);

            container.appendChild(row);

            // Ensure AvatarSystem is initialized
            if (window.AvatarSystem) {
                if (!window.AvatarSystem.isRunning) window.AvatarSystem.init();
                // If already running, MutationObserver should pick it up.
                // But let's force a check to be sure for test.
                // window.AvatarSystem.mutationObserver might be async.
            }
        """)

        # Wait for render updates (MutationObserver -> IntersectionObserver -> Render Loop)
        page.wait_for_timeout(3000)

        # Take screenshot
        screenshot_path = os.path.join(cwd, 'verification/visual_check.png')
        page.screenshot(path=screenshot_path)
        print(f"Screenshot saved to {screenshot_path}")

        browser.close()

if __name__ == "__main__":
    run()

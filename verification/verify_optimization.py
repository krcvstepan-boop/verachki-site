import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Mock THREE
        await page.add_init_script("""
            window.THREE = {
                WebGLRenderer: class {
                    constructor() {
                        this.domElement = document.createElement('canvas');
                    }
                    setSize() {}
                    setPixelRatio() {}
                    setClearColor() {}
                    render() {}
                    setScissorTest() {}
                    clear() {}
                    setViewport() {}
                    setScissor() {}
                    dispose() {}
                },
                Scene: class { add() {} remove() {} },
                PerspectiveCamera: class { position = { z: 0 }; updateProjectionMatrix() {} },
                AmbientLight: class {},
                PointLight: class { position = { set: () => {} }; },
                Group: class { add() {} rotation = { x: 0, y: 0 }; traverse() {} },
                SphereGeometry: class { attributes = { position: { count: 10, fromBufferAttribute: () => {}, setXYZ: () => {} } }; computeVertexNormals() {} dispose() {} },
                Vector3: class { fromBufferAttribute() {}; multiplyScalar() {}; normalize() {} },
                ShaderMaterial: class { dispose() {} },
                Mesh: class { rotation = { set: () => {} }; scale = { setScalar: () => {} }; material = { dispose: () => {} }; geometry = { dispose: () => {} } },
                BufferGeometry: class { setAttribute() {} dispose() {} },
                BufferAttribute: class {},
                PointsMaterial: class { dispose() {} },
                Points: class { material = { dispose: () => {} }; geometry = { dispose: () => {} } },
                Color: class {},
                AdditiveBlending: 2,
                FrontSide: 0,
                MathUtils: { randFloat: () => 0.5 }
            };
        """)

        # Mock Appwrite
        await page.add_init_script("""
            window.Appwrite = {
                Client: class {
                    setEndpoint() { return this; }
                    setProject() { return this; }
                    subscribe() {}
                },
                Account: class {
                    get() { return Promise.reject('No user'); }
                    createEmailPasswordSession() {}
                    create() {}
                    deleteSession() {}
                },
                Databases: class {
                    listDocuments() { return Promise.resolve({ documents: [] }); }
                    createDocument() {}
                    updateDocument() {}
                    deleteDocument() {}
                },
                Storage: class {
                    getFileView() { return ''; }
                    createFile() {}
                },
                ID: { unique: () => 'id-' + Math.random() },
                Query: { orderAsc: () => {}, limit: () => {}, equal: () => {} }
            };
        """)

        # Stats Monitoring
        await page.add_init_script("""
            window.stats = {
                querySelectorAllCalls: 0,
                getBoundingClientRectCalls: 0
            };

            const originalQSA = document.querySelectorAll;
            document.querySelectorAll = function(...args) {
                if (args[0] === '.soul-avatar-placeholder') {
                    window.stats.querySelectorAllCalls++;
                }
                return originalQSA.apply(this, args);
            };

            const originalGBRC = Element.prototype.getBoundingClientRect;
            Element.prototype.getBoundingClientRect = function(...args) {
                if (this.classList && this.classList.contains('soul-avatar-placeholder')) {
                    window.stats.getBoundingClientRectCalls++;
                }
                return originalGBRC.apply(this, args);
            };
        """)

        cwd = os.getcwd()
        # Load page
        await page.goto(f'file://{cwd}/index.html')

        # Reveal App Interface (crucial for IntersectionObserver)
        await page.evaluate("""
            document.getElementById('app-interface').classList.remove('hidden');
            document.getElementById('messages-container').style.display = 'block';
            document.getElementById('messages-container').style.height = '100vh';
            document.getElementById('messages-container').style.overflowY = 'scroll';
        """)

        # Add dummy messages
        await page.evaluate("""
            const container = document.getElementById('messages-container');
            if (container) {
                container.innerHTML = '';
                for (let i = 0; i < 50; i++) {
                    const row = document.createElement('div');
                    row.className = 'message-row';

                    const avatar = document.createElement('div');
                    avatar.className = 'soul-avatar-placeholder';
                    avatar.dataset.user = 'user' + i;

                    // Style to ensure some are visible and some are not
                    row.style.height = '100px';
                    row.style.width = '100%';
                    row.style.display = 'block';
                    row.style.marginBottom = '10px';

                    row.appendChild(avatar);
                    container.appendChild(row);
                }
            }
        """)

        # Init AvatarSystem
        await page.evaluate("""
            if (window.AvatarSystem) {
                 window.AvatarSystem.init();
            }
        """)

        # Wait 1 second for intersections to trigger and loop to run
        await asyncio.sleep(1)

        # Get stats
        stats = await page.evaluate("window.stats")
        print(f"querySelectorAll Calls: {stats['querySelectorAllCalls']}")
        print(f"getBoundingClientRect Calls: {stats['getBoundingClientRectCalls']}")

        await browser.close()

if __name__ == '__main__':
    asyncio.run(run())

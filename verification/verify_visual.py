import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(viewport={'width': 375, 'height': 812})
        page = await context.new_page()
        cwd = os.getcwd()
        await page.goto(f"file://{cwd}/index.html")

        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        # Stub loadMessages to prevent overwriting our test data
        await page.evaluate("""
            window.loadMessages = function() {
                console.log('loadMessages stub called - preventing default loading');
                // We do nothing here, letting our manual population stick
            };
        """)

        # Show app (this calls AvatarSystem.init())
        await page.evaluate("showApp()")

        # Populate with messages
        await page.evaluate("""
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            for(let i=0; i<5; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                row.style.marginBottom = '20px';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'User' + i;
                avatar.style.width = '60px';
                avatar.style.height = '60px';
                avatar.style.background = 'rgba(0,0,0,0.1)'; // Visual debug background

                const msg = document.createElement('div');
                msg.className = 'message';
                msg.innerText = 'Hello verification ' + i;

                row.appendChild(avatar);
                row.appendChild(msg);
                container.appendChild(row);
            }
        """)

        # Wait for Three.js to render
        await asyncio.sleep(2)

        await page.screenshot(path="verification/screenshot_fixed.png")
        print("Screenshot saved to verification/screenshot_fixed.png")

        # Also verify avatars are visible via JS state
        visible_count = await page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible avatars: {visible_count}")

        if visible_count == 0:
             print("FAIL: No avatars visible.")
             exit(1)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

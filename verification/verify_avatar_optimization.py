import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Set viewport
        context = await browser.new_context(viewport={'width': 1280, 'height': 720})
        page = await context.new_page()
        cwd = os.getcwd()
        await page.goto(f"file://{cwd}/index.html")

        # Mock console
        page.on("console", lambda msg: print(f"PAGE LOG: {msg.text}"))

        try:
            await page.wait_for_load_state("networkidle", timeout=5000)
        except:
            pass

        # Check initial state
        await page.evaluate("console.log('App interface hidden?', document.getElementById('app-interface').classList.contains('hidden'))")

        # Switch to app interface
        await page.evaluate("showApp()")
        await asyncio.sleep(0.5)

        await page.evaluate("console.log('App interface hidden after showApp?', document.getElementById('app-interface').classList.contains('hidden'))")

        # Generate messages
        await page.evaluate("""
            const container = document.getElementById('messages-container');
            container.innerHTML = '';
            console.log('Generating messages...');
            for(let i=0; i<100; i++) {
                const row = document.createElement('div');
                row.className = 'message-row';
                row.style.height = '100px';
                row.style.marginBottom = '10px';

                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = 'User' + i;
                avatar.style.width = '50px';
                avatar.style.height = '50px';
                avatar.style.display = 'block';
                avatar.style.background = 'red'; // Make sure it has visual presence?

                row.appendChild(avatar);
                container.appendChild(row);
            }
            container.scrollTop = 0;
            console.log('Messages generated. Total placeholders:', document.querySelectorAll('.soul-avatar-placeholder').length);
        """)

        # Wait for observers
        await asyncio.sleep(2)

        # Check visible avatars count
        visible_count = await page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible avatars count (top): {visible_count}")

        # Check if observer is even running
        is_observing = await page.evaluate("!!window.AvatarSystem.observer")
        print(f"Observer initialized: {is_observing}")

        if visible_count == 0:
             # Debug why
             await page.evaluate("""
                 const placeholders = document.querySelectorAll('.soul-avatar-placeholder');
                 if(placeholders.length > 0) {
                     const rect = placeholders[0].getBoundingClientRect();
                     console.log('First placeholder rect:', rect.top, rect.bottom, rect.height, rect.width);
                     console.log('Window innerHeight:', window.innerHeight);
                     console.log('Container scroll:', document.getElementById('messages-container').scrollTop);
                 }
             """)
             print("FAIL: No visible avatars detected.")
             # Don't exit yet, check bottom

        # Scroll to bottom
        await page.evaluate("""
            const container = document.getElementById('messages-container');
            container.scrollTop = container.scrollHeight;
            console.log('Scrolled to bottom. New scrollTop:', container.scrollTop);
        """)

        await asyncio.sleep(2)

        visible_count_bottom = await page.evaluate("window.AvatarSystem.visibleAvatars.size")
        print(f"Visible avatars count (bottom): {visible_count_bottom}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

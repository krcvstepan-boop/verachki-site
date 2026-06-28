import asyncio
from playwright.async_api import async_playwright
import os
import json

async def run_with_logs():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        await page.route("**/v1/**", lambda route: route.fulfill(
            status=200,
            content_type="application/json",
            body=json.dumps({"documents": [], "total": 0, "message": "mocked", "code": 200})
        ))

        await page.goto('http://localhost:8080')

        await page.evaluate("""
            window.checkSession = () => Promise.resolve();
            state.user = { email: 'user@example.com', name: 'User' };
            state.profile = { $id: 'user_profile_id', username: 'User', email: 'user@example.com', rank: 'Наблюдатель' };

            // Show App
            document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
            const app = document.getElementById('app-interface');
            if (app) app.classList.remove('hidden');
        """)

        # Trigger some error toasts to see them in UI
        await page.evaluate("""
            document.getElementById('p-about-edit').value = 'A'.repeat(501);
            saveMyProfile();

            // Wait for toast to appear then take screenshot
        """)

        await asyncio.sleep(1)
        await page.screenshot(path="verification/ui_check.png")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run_with_logs())

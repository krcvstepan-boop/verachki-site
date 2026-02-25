import asyncio
from playwright.async_api import async_playwright
import os

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Mock Appwrite to prevent errors
        await page.add_init_script("""
            window.Appwrite = {
                Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() {} },
                Account: class { get() { return Promise.resolve({}); } createEmailPasswordSession() {} deleteSession() {} create() {} },
                Databases: class { listDocuments() { return Promise.resolve({documents: []}); } createDocument() {} updateDocument() {} deleteDocument() {} },
                Storage: class { createFile() {} getFileView() {} },
                ID: { unique: () => 'unique_id' },
                Query: { equal: () => {}, orderAsc: () => {}, limit: () => {} }
            };
            window.AvatarSystem = { init: () => {}, updateAvatar: () => {}, renderProfileAvatar: () => {} };
        """)

        # Go to the page
        await page.goto(f"file://{os.getcwd()}/index.html")

        # Mock window.prompt
        await page.evaluate("window.prompt = (msg) => 'mock_token'")

        print("Testing askMistral with interactive mode...")
        # Call askMistral interactively
        # We need to mock fetch first to avoid network errors and verify the token is sent
        await page.route("**/api-inference.huggingface.co/**", lambda route: route.fulfill(
            status=200,
            body='[{"generated_text": "Mock Response"}]',
            headers={"Content-Type": "application/json"}
        ))

        # We need to manually clear localStorage first just in case
        await page.evaluate("localStorage.removeItem('HF_TOKEN')")

        # Since askMistral is async, we call it and wait
        # Pass prompt="test", isInteractive=true
        # Note: script.js might not be loaded immediately if we don't wait for it
        # But Playwright's goto usually waits for load event.

        # Check if askMistral is defined
        is_defined = await page.evaluate("typeof askMistral !== 'undefined'")
        if not is_defined:
            print("❌ askMistral is not defined. Script might not be loaded.")
            exit(1)

        result = await page.evaluate("askMistral('test', true)")

        # Verify token is in localStorage
        token = await page.evaluate("localStorage.getItem('HF_TOKEN')")
        if token == 'mock_token':
            print("✅ Token saved to localStorage successfully.")
        else:
            print(f"❌ Token NOT saved. Found: {token}")
            exit(1)

        print("Testing 401 Unauthorized handling...")
        # Mock 401 response
        await page.route("**/api-inference.huggingface.co/**", lambda route: route.fulfill(
            status=401,
            body='{"error": "Unauthorized"}'
        ))

        # Call again, should fail and clear token
        await page.evaluate("askMistral('test', false)") # false or true, should clear either way

        token_after_401 = await page.evaluate("localStorage.getItem('HF_TOKEN')")
        if token_after_401 is None:
            print("✅ Token cleared from localStorage on 401.")
        else:
            print(f"❌ Token NOT cleared. Found: {token_after_401}")
            exit(1)

        await browser.close()

if __name__ == "__main__":
    asyncio.run(run())

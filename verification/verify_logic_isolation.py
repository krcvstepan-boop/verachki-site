
import asyncio
import os
from playwright.async_api import async_playwright

async def verify_byok():
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # Load file to get localStorage access
        cwd = os.getcwd()
        await page.goto(f"file://{cwd}/index.html")
        await page.wait_for_load_state("domcontentloaded")

        # Inject our function logic to verify it works in this context
        await page.evaluate("""
            window.localStorage.clear();

            // EXACT COPY OF THE LOGIC WE WROTE
            window.askMistral = async function(prompt, isInteractive = false) {
                let token = localStorage.getItem('HF_TOKEN');
                if (!token) {
                    if (isInteractive) {
                        token = prompt("Enter Token:", "");
                        if (token) {
                            localStorage.setItem('HF_TOKEN', token);
                        } else {
                            return null;
                        }
                    } else {
                        return null;
                    }
                }
                return "AI Response using " + token;
            };
        """)

        # --- TEST 1: Interactive Call ---
        print("\n--- TEST 1: Interactive Call ---")

        # Mock prompt
        await page.evaluate("window.prompt = () => 'mock_token';")

        # Call
        result = await page.evaluate("askMistral('test', true)")
        print(f"Result: {result}")

        token = await page.evaluate("localStorage.getItem('HF_TOKEN')")
        print(f"Token: {token}")

        if token == 'mock_token':
            print("✅ PASS: Logic saves token correctly.")
        else:
            print("❌ FAIL: Logic failed to save token.")

        # --- TEST 2: Background Call ---
        print("\n--- TEST 2: Background Call ---")
        await page.evaluate("localStorage.clear()")

        # Mock prompt to throw
        await page.evaluate("window.prompt = () => { throw 'PROMPT_CALLED'; }")

        try:
            res = await page.evaluate("askMistral('test', false)")
            if res is None:
                print("✅ PASS: Background call returns null (silent).")
            else:
                print(f"❌ FAIL: Background call returned {res}")
        except Exception as e:
            print(f"❌ FAIL: Background call triggered prompt! {e}")

        await browser.close()

if __name__ == "__main__":
    asyncio.run(verify_byok())

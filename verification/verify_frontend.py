
import os
from playwright.sync_api import sync_playwright

def run(playwright):
    browser = playwright.chromium.launch(headless=True)
    page = browser.new_page()

    # Load the page
    # We use file:// protocol
    cwd = os.getcwd()
    page.goto(f"file://{cwd}/index.html")

    # Wait for script to load
    page.wait_for_timeout(1000)

    # Define dialog handler
    def handle_dialog(dialog):
        print(f"Dialog message: {dialog.message}")
        if "Введите Hugging Face Token" in dialog.message:
            print("Dialog detected correctly!")
            dialog.accept("mock_token_from_playwright")
        else:
            dialog.dismiss()

    page.on("dialog", handle_dialog)

    # Trigger askMistral manually
    # We need to expose the function or just run it in evaluation
    # Since askMistral is defined in the global scope (script.js is not a module), we can access it via window.
    # But script.js is defer, so we wait.

    # We also need to mock localStorage to ensure it's empty first
    page.evaluate("localStorage.clear()")

    print("Triggering askMistral interactively...")
    # This should trigger the prompt
    result = page.evaluate("askMistral('Hello', true)")
    print(f"Result from askMistral: {result}")

    # Now check if token is stored
    token = page.evaluate("localStorage.getItem('HF_TOKEN')")
    print(f"Stored token: {token}")

    if token == "mock_token_from_playwright":
        print("SUCCESS: Token was prompt-ed and stored.")
    else:
        print("FAILURE: Token not stored.")

    # Screenshot just to show the page loaded
    page.screenshot(path="verification/frontend_check.png")

    browser.close()

with sync_playwright() as playwright:
    run(playwright)

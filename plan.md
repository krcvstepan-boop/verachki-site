1. **Remove hardcoded HuggingFace API key**
   - The HF token is hardcoded in `script.js` on lines 11-13. This is a critical security vulnerability.
   - We will replace it with a Bring Your Own Key (BYOK) model. We'll store the key in `localStorage` under `HF_TOKEN`.
   - In `askMistral`, if the token is not present in `localStorage` and `isInteractive` is true, we will use `window.prompt` to ask the user to enter their API key, save it to `localStorage`, and use it.
   - We will modify `askMistral` to accept an `isInteractive` boolean parameter.
   - We will also add a way to clear the token if the AI API returns a 401 Unauthorized, and throw an error so the next call prompts again.

2. **Update script.js function signatures and logic**
   - Find all calls to `askMistral` and update them to pass `isInteractive` appropriately.
   - The direct trigger from sending a message should set `isInteractive` to `true`.
   - The background triggers should set `isInteractive` to `false` to avoid random `window.prompt` popups.
   - Modify the `askMistral(prompt)` signature to `askMistral(promptText, isInteractive)`.

3. **Verify the change**
   - I will run standard validation checks (lint/test equivalents if they exist, or node --check).
   - I will use `verification/verify_changes.py` or write a custom test to ensure the prompt logic behaves correctly.

4. **Complete pre-commit steps to ensure proper testing, verification, review, and reflection are done.**
   - Run `pre_commit_instructions`.

5. **Commit and Submit**
   - Title: "🛡️ Sentinel: [CRITICAL] Fix hardcoded API key"

# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Key Exposure and BYOK Pattern
**Vulnerability:** A Hugging Face API Token was hardcoded directly in `script.js` (split across two variables `keyP1` and `keyP2` and concatenated), exposing the API key to any client loading the script.
**Learning:** Hardcoded secrets in client-side code are inherently exposed to users. Security by obscurity (e.g., splitting keys) is ineffective. 3rd-party API keys must never be hardcoded or concatenated in client-side JavaScript.
**Prevention:** Use a Bring Your Own Key (BYOK) model storing tokens securely in `localStorage` or proxy requests through a secure backend server. Implement prompts specifically for direct user interactions to acquire the token securely without interrupting background processes.

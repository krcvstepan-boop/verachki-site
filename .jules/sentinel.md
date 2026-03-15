# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).
## 2024-05-25 - Prevent Hardcoded API Keys (Hugging Face)
**Vulnerability:** Hugging Face API tokens were hardcoded as global constants (`keyP1`, `keyP2`, `HF_TOKEN`) and concatenated in client-side JavaScript (`script.js`).
**Learning:** Hardcoding sensitive tokens in client-side code, even when split into parts, exposes them to anyone who inspects the source code. This allows malicious actors to misuse the API under the application's account, potentially leading to unauthorized data access, quota exhaustion, or unexpected billing costs.
**Prevention:** Never hardcode API keys or sensitive tokens in client-side code. Use a Bring Your Own Key (BYOK) model where users provide their own tokens, which are stored securely in `localStorage` or `sessionStorage`. For API keys that must be provided by the application, proxy requests through a secure backend server that holds the keys as environment variables.

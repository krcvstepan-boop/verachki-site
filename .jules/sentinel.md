# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Key in Client Code
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js` (split into `keyP1` and `keyP2` and concatenated as `HF_TOKEN`). Anyone inspecting the source code could extract and misuse the token for unauthorized API requests.
**Learning:** Hardcoding secrets in client-side code exposes them completely. Splitting strings does not prevent discovery, it merely obfuscates it temporarily.
**Prevention:** Never include sensitive tokens or API keys in client-side JavaScript. Implement a "Bring Your Own Key" (BYOK) model storing tokens securely in the user's `localStorage`, or route requests through a secure backend proxy that handles authentication.

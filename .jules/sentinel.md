# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Key in Client Code
**Vulnerability:** Hugging Face API key was hardcoded in `script.js` directly, exposing it to any user inspecting the client-side code.
**Learning:** External API credentials must never be hardcoded or concatenated in client-side JS files.
**Prevention:** Implemented a Bring Your Own Key (BYOK) model storing tokens in `localStorage` which dynamically queries users via `window.prompt` when needed. Alternatively, request proxies through a secure backend should be used.

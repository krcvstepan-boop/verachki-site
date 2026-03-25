# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2026-03-25 - Hardcoded API Key Exposure
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js` by concatenating two string segments (`keyP1` and `keyP2`) and exposing the token globally.
**Learning:** Hardcoding any secrets in client-side code exposes them to anyone who accesses the application. Concatenation does not prevent discovery.
**Prevention:** Avoid hardcoding keys. Use a "Bring Your Own Key" (BYOK) model for external integrations on the client side, storing user-provided tokens securely in `localStorage` or session, or alternatively, proxy requests through a secured backend.

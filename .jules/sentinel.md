# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2026-04-12 - Removal of Hardcoded Hugging Face Token & BYOK Implementation
**Vulnerability:** A Hugging Face API token was hardcoded in the frontend `script.js`. Since this is a client-side application, the token was exposed to anyone visiting the site, risking quota exhaustion and unauthorized use.
**Learning:** External API keys should never be committed to source code. For serverless/client-only apps, a "Bring Your Own Key" (BYOK) model is a secure alternative to hardcoding or proxying if a backend isn't feasible.
**Prevention:** Use `localStorage` to store user-provided keys and `window.prompt` (or a dedicated UI) to collect them when missing. Ensure the UI clearly distinguishes between system-triggered calls and user-interactive calls to avoid unexpected popups.

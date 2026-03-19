# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2025-02-18 - Hardcoded API Keys in Client-Side JavaScript
**Vulnerability:** Third-party API keys (HuggingFace token) were hardcoded and concatenated in client-side JavaScript (`script.js`).
**Learning:** Client-side JavaScript is accessible to all users. Hardcoded keys expose external API quotas and backend systems to malicious use.
**Prevention:** Never hardcode secrets in client-side code. Use a Bring Your Own Key (BYOK) flow stored securely in `localStorage` or proxy requests through a secure backend server.

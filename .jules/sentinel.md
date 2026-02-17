# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded Credentials in Client-Side Code
**Vulnerability:** `HF_TOKEN` was hardcoded in `script.js` to enable AI features. This exposed the private key to all users.
**Learning:** Client-side applications cannot securely store secrets. Obfuscation (splitting strings) is not security.
**Prevention:** Implement a "Bring Your Own Key" (BYOK) pattern where users input their own API keys, stored locally in `localStorage`, or use a backend proxy for API calls.

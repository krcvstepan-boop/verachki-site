# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Keys in Client-Side Code
**Vulnerability:** A Hugging Face API token was hardcoded directly in `script.js`. Splitting the string into parts provided no security, as it was easily reconstructible by anyone viewing the source.
**Learning:** Client-side applications cannot safely store secrets. API keys must either be proxied through a backend or provided by the user (Bring Your Own Key).
**Prevention:** Removed hardcoded keys. Implemented a pattern where the user is prompted to enter their own token, which is then stored in `localStorage`.

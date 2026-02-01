# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-24 - Client-Side Secret Management via LocalStorage
**Vulnerability:** Hardcoded API keys (Hugging Face Token) were committed in `script.js`, exposing the developer's quota to all users.
**Learning:** In a static site architecture (no backend), "secrets" cannot be safely stored in code or environment variables.
**Prevention:** Shifted to a "Bring Your Own Key" (BYOK) model. Credentials are now stored in the user's `localStorage` and requested via prompt when missing. This avoids exposure in the repo while preserving functionality for authorized users.

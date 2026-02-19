# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-24 - Hardcoded API Secrets in Client-Side Code
**Vulnerability:** API keys for third-party services (Hugging Face) were hardcoded in `script.js`, exposing them to all users and potential abuse.
**Learning:** Client-side applications cannot securely store secrets. Obfuscation (splitting strings) is ineffective.
**Prevention:** Use a "Bring Your Own Key" (BYOK) pattern where the user provides their own API key, stored in `localStorage`. The application should handle missing keys gracefully by disabling dependent features.

# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Secrets in Client-Side Code
**Vulnerability:** A Hugging Face API token was hardcoded in `script.js` constants. Since the application is client-side only (HTML/JS), this exposed the credential to all users.
**Learning:** You cannot secure API keys in a purely client-side application without a backend proxy. Splitting strings (`key1 + key2`) offers zero security against static analysis.
**Prevention:** Implement a "Bring Your Own Key" (BYOK) pattern where the user provides the key (stored in `localStorage`), or move the API interaction to a backend/edge function.

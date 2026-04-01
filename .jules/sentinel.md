# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded Secrets
**Vulnerability:** Hugging Face API tokens were hardcoded directly into the client-side JavaScript (`script.js`), exposing them to anyone viewing the source code.
**Learning:** Hardcoding 3rd-party API keys in client-side code makes them trivially accessible and leads to unauthorized usage/abuse.
**Prevention:** Use a Bring Your Own Key (BYOK) model, storing the token in `localStorage` and prompting the user for it if missing, or use a secure backend proxy to make API requests.

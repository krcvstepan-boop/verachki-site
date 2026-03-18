# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded 3rd-Party API Keys
**Vulnerability:** A Hugging Face API token was hardcoded directly into the client-side JavaScript (`script.js`), exposing it to anyone inspecting the code.
**Learning:** Hardcoding 3rd-party API keys on the frontend is a critical security risk. It allows unauthorized users to consume the API quota or access services maliciously.
**Prevention:** Use a Bring Your Own Key (BYOK) model where users provide their own token, which is then stored securely in `localStorage`, or proxy API requests through a secure backend that handles the token.

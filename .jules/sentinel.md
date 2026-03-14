# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Key in Client Code
**Vulnerability:** A third-party API key (Hugging Face token) was hardcoded in the client-side JavaScript (`script.js`), exposing it to anyone viewing the source code.
**Learning:** Hardcoding API keys on the frontend allows unauthorized access and potential abuse of the associated account and its resources. The "Bring Your Own Key" (BYOK) model provides a secure alternative for client-side applications interacting directly with third-party services.
**Prevention:** Never hardcode API keys in client-side code. Use a BYOK approach, prompting users for their own tokens and storing them locally (e.g., `localStorage`), or proxy requests through a secure backend that holds the key.

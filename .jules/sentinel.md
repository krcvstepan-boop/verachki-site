# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Keys and BYOK Strategy
**Vulnerability:** A Hugging Face API token used for AI inference was hardcoded in the frontend JavaScript codebase and exposed to all clients.
**Learning:** Hardcoding API keys in the client side guarantees they will be leaked, potentially resulting in unauthorized usage and quota exhaustion.
**Prevention:** Use a Bring Your Own Key (BYOK) strategy, requesting the user for their API key and storing it in `localStorage` for future use, or proxying the API requests through a secure backend that holds the key.

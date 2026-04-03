# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded External API Keys
**Vulnerability:** A Hugging Face API key (`HF_TOKEN`) was hardcoded in `script.js` (concatenated via `keyP1` and `keyP2`). This exposes the secret to all clients, allowing potential abuse and cost implications.
**Learning:** Client-side JavaScript can never securely hold API secrets for third-party services. Obfuscation (like string concatenation) provides no actual security.
**Prevention:** Implemented a Bring Your Own Key (BYOK) model storing the token securely in `localStorage`, requesting it only when explicitly needed by user interaction. Alternative prevention is to proxy requests through a secure backend that handles authentication.

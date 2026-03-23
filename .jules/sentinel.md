# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded External API Tokens
**Vulnerability:** External API tokens (e.g., HuggingFace token for Mistral) were hardcoded and concatenated in client-side code (`script.js`). Anyone inspecting the source code could extract and misuse the token, leading to unauthorized API usage and potential billing or rate-limiting issues.
**Learning:** Client-side JavaScript cannot securely store secrets. Even obfuscation or splitting strings does not prevent extraction.
**Prevention:** Never hardcode 3rd-party API keys in the frontend. Use a Bring Your Own Key (BYOK) model (e.g., storing user-provided tokens in `localStorage`) or proxy requests through a secure backend server that manages the secrets.

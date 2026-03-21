# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded 3rd-Party API Tokens
**Vulnerability:** 3rd-party API keys (HuggingFace token) were hardcoded in the client-side JavaScript (`script.js`), exposing them to anyone viewing the source code.
**Learning:** Hardcoding secrets in client-side code completely bypasses access controls. Even obfuscated string concatenation (`keyP1 + keyP2`) is easily compromised on the frontend.
**Prevention:** 3rd-party API tokens must never be hardcoded or concatenated in client-side code. Instead, use a Bring Your Own Key (BYOK) model storing tokens in `localStorage`, or proxy requests through a secure backend.

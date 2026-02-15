# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-22 - Client-Side Secret Exposure
**Vulnerability:** A Hugging Face API token was hardcoded in `script.js` (concatenated string parts) and exposed to all clients.
**Learning:** In static site architectures without a backend, developers often resort to client-side API calls, leading to secret exposure. Obfuscation (splitting strings) is security theater and ineffective against static analysis.
**Prevention:** Use a backend proxy for API calls or a "Bring Your Own Key" (BYOK) architecture where users provide their own credentials for optional features. Never commit secrets to client-side code.

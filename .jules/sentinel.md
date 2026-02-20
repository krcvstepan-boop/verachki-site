# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Key Exposure
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js` and split into two variables (`keyP1`, `keyP2`) to attempt obfuscation. Any user could inspect the source code and retrieve the key to abuse the API quota.
**Learning:** Client-side obfuscation of secrets is ineffective as the code must eventually reconstruct the secret to use it. In a static site architecture without a backend proxy, secrets cannot be hidden.
**Prevention:** Implement a "Bring Your Own Key" (BYOK) model where the user provides their own API key, which is stored in `localStorage`. Alternatively, use a backend service to proxy requests and manage secrets securely.

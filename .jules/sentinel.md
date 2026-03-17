# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded HuggingFace API Key
**Vulnerability:** The HuggingFace API token (`HF_TOKEN`) was hardcoded in `script.js` by concatenating two string parts. This exposes the secret to anyone viewing the client-side JavaScript, potentially leading to unauthorized usage, quota exhaustion, and billing issues.
**Learning:** Concatenation or obfuscation of API keys on the client-side does not provide security, as the final key is still present in the executable code.
**Prevention:** Never hardcode 3rd-party API keys in client-side code. Use a Bring Your Own Key (BYOK) model where the user provides their own token and it is stored securely on the client side (e.g., in `localStorage`), or proxy requests through a secure backend that handles authentication.

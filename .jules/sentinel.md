# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded 3rd-Party API Keys in Frontend Code
**Vulnerability:** A HuggingFace API token (`HF_TOKEN`) was hardcoded directly in the client-side JavaScript (`script.js`), split into two concatenated strings to evade basic scanners. Anyone viewing the source could extract and abuse this key.
**Learning:** Hardcoding secrets in frontend code, regardless of obfuscation techniques like string splitting, is inherently insecure. All client-side code is fully visible to the user.
**Prevention:** Use a Bring Your Own Key (BYOK) model for 3rd-party services where users provide their own tokens (e.g., via `localStorage`), or proxy requests through a secure backend that holds the secret.

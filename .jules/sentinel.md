# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded External API Secrets
**Vulnerability:** The Hugging Face API token (`HF_TOKEN`) was hardcoded directly in `script.js` and shipped to the client-side. This exposed the secret to any user examining the source code, allowing malicious actors to use the token to make unauthorized requests to the Hugging Face API, potentially resulting in quota exhaustion or unauthorized access.
**Learning:** Client-side JavaScript cannot securely store or hide secrets used for external APIs because the entire source code is accessible by the browser. Obfuscating the token (e.g., splitting it into `keyP1` and `keyP2`) is security theater and does not prevent extraction.
**Prevention:** Never hardcode secrets in client-side code. For external APIs accessed directly from the client, implement a "Bring Your Own Key" (BYOK) flow where users provide their own tokens via `window.prompt` and store them in `localStorage`. Alternatively, route requests through a secure backend server that holds the secret.

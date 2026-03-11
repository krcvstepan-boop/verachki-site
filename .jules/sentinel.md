# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded Hugging Face Token in Client Code
**Vulnerability:** A Hugging Face API token (`HF_TOKEN`) was hardcoded into the client-side JavaScript (`script.js`) by splitting it into two variables (`keyP1`, `keyP2`) and concatenating them. This is insecure as any user can inspect the source code, extract the token, and use it maliciously to exhaust API quotas or perform unauthorized actions.
**Learning:** Obfuscating a token via string concatenation does not provide security on the client side. The browser still needs the full string to make the API request, meaning the raw token is fully exposed to DevTools and network inspection.
**Prevention:** Never hardcode API keys or secrets in client-side code. Instead, implement a Bring Your Own Key (BYOK) model where the user provides their own key (stored locally via `localStorage`), or proxy requests through a secure, authenticated backend server that securely manages the API key as an environment variable.

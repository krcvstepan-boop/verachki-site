# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded Hugging Face API Token
**Vulnerability:** A Hugging Face API token (`HF_TOKEN`) was hardcoded in `script.js` by concatenating two strings. This exposed the token to anyone viewing the client-side source code, risking quota abuse.
**Learning:** Obfuscation (string splitting) is not security. Client-side applications cannot securely store secrets without a backend or proxy.
**Prevention:** Implemented a "Bring Your Own Key" (BYOK) pattern. The app now checks `localStorage` for the token and prompts the user to enter it securely if missing, storing it only in their local browser storage.

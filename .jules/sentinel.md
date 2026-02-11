# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-24 - Hardcoded API Keys in Client-Side Code
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js` as a global variable.
**Learning:** Client-side applications cannot securely store secrets. Even obfuscation (splitting strings) is trivial to reverse.
**Prevention:** Implement a "Bring Your Own Key" (BYOK) pattern where the user provides the key at runtime (via prompt/settings) and it is stored in `localStorage` or `sessionStorage`. For static sites without a backend proxy, this shifts the secret management responsibility to the user.

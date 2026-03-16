# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-06-15 - Hardcoded API Keys in Client-Side JavaScript
**Vulnerability:** A third-party API key (HuggingFace token) was hardcoded in `script.js` using simple string concatenation (`const HF_TOKEN = keyP1 + keyP2;`), making it publicly accessible to anyone viewing the source code.
**Learning:** Obfuscation by splitting strings does not provide security for client-side keys. If code runs in the browser, any secrets it contains are fully exposed.
**Prevention:** Never store third-party API keys in client-side code. Use a Bring Your Own Key (BYOK) model where the user provides their own key (stored locally in `localStorage`), or proxy the requests through a secure backend server where the key is kept secret.

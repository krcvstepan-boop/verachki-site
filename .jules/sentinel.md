# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Keys in Client-Side Code
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js` and split into two strings (`keyP1` + `keyP2`) to evade simple scanners. This still exposed the key to anyone viewing the source.
**Learning:** Obfuscation (splitting strings) is not security. Client-side apps cannot safely hold secrets.
**Prevention:** Use a "Bring Your Own Key" (BYOK) architecture for client-side AI features, or proxy requests through a secure backend (e.g., Appwrite Functions) where secrets can be stored in environment variables.

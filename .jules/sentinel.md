# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-24 - Hardcoded AI API Tokens
**Vulnerability:** A Hugging Face API token was hardcoded in `script.js` (split into two parts to avoid simple grep). This allows anyone with access to the source code to use the developer's quota.
**Learning:** Obfuscation (splitting strings) is not security. Client-side applications cannot securely store global secrets.
**Prevention:** Implement "Bring Your Own Key" (BYOK) flows. Store user-provided keys in `localStorage` and prompt for them only during interactive sessions to maintain a smooth background experience.

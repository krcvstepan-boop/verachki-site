# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Key in Client Code
**Vulnerability:** HuggingFace API tokens were hardcoded directly in `script.js` (`keyP1`, `keyP2`, `HF_TOKEN`). Although partially obfuscated by string concatenation, they are fully exposed to anyone viewing the client-side source code.
**Learning:** Client-side JavaScript cannot securely store secrets. Any API key embedded in the frontend can be extracted and abused by malicious actors.
**Prevention:** Implement a Bring Your Own Key (BYOK) model where users provide their own tokens which are stored locally via `localStorage`, or route requests through a secure backend proxy.

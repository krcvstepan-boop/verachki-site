# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Key Exposure
**Vulnerability:** Hugging Face API tokens were hardcoded globally in `script.js` and split into chunks (`keyP1` + `keyP2`). This exposed the secret token directly to anyone viewing the client-side source code.
**Learning:** Concatenating split strings is security theater; it provides zero protection against source code inspection. 3rd-party API keys must never exist in client-side code.
**Prevention:** Implement a Bring Your Own Key (BYOK) model storing keys in `localStorage`, or route requests through a secure backend proxy to protect credentials.

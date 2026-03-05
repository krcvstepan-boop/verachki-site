# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2026-03-05 - Hardcoded 3rd-Party API Keys
**Vulnerability:** A third-party AI integration API key (HuggingFace token) was constructed and hardcoded directly in the client-side JavaScript (`script.js`), completely exposing it to anyone viewing the source.
**Learning:** Constructing a key from multiple variables (`keyP1 + keyP2`) in the client does not hide it from users, as all JavaScript is downloaded and readable by the client browser.
**Prevention:** Implement a 'Bring Your Own Key' (BYOK) model for client-side applications by prompting the user for their token and storing it securely in `localStorage`, or proxy API requests through a secured backend service.

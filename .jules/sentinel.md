# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded API Secrets in Client-Side Code
**Vulnerability:** A paid API key (Hugging Face) was hardcoded in `script.js`, exposing it to all users and potential scrapers.
**Learning:** Client-side apps without a backend proxy cannot securely hold secrets. Even obfuscation (splitting strings) is easily reversed.
**Prevention:** Use a "Bring Your Own Key" (BYOK) model where the user provides the key via `window.prompt` and it is stored in `localStorage`, shifting the cost and liability to the user.

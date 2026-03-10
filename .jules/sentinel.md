# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded External API Tokens
**Vulnerability:** Hugging Face API tokens (`keyP1`, `keyP2`, `HF_TOKEN`) were hardcoded directly in `script.js`. Any user with access to the client-side JavaScript could extract these tokens and use the API under the application's billing account or identity.
**Learning:** Hardcoding secrets in client-side code, even when obfuscated by simple concatenation, provides no security. The client environment must be treated as untrusted.
**Prevention:** Implement a "Bring Your Own Key" (BYOK) model where users input their own tokens, which are then stored in their local environment (e.g., `localStorage`). Alternatively, proxy requests requiring secrets through a secure backend server where the token can be safely managed as an environment variable.

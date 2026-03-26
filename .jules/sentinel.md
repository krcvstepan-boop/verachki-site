# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded External API Keys
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js`, split across multiple variables (`keyP1` and `keyP2`) and combined to bypass simple regex scanners.
**Learning:** Obfuscating secrets by string concatenation provides no real security on the client side. Any token bundled with the client can be intercepted and abused.
**Prevention:** Never commit API keys or store them in client-side code. Use a Bring Your Own Key (BYOK) model storing tokens in `localStorage`, or proxy requests through a secure backend.

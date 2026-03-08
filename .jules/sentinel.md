# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded 3rd-Party API Keys in Client-Side Code
**Vulnerability:** Hugging Face API tokens (`keyP1` and `keyP2` concatenated into `HF_TOKEN`) were hardcoded in `script.js` and exposed in the client-side bundle. This allows any user to steal the key and consume the API quota or access restricted resources.
**Learning:** Concatenating keys or trying to obfuscate them in client-side code is ineffective because the final value is visible in the network tab or accessible via the browser console. Client-side applications should never hold raw secrets for 3rd party APIs.
**Prevention:** Use a 'Bring Your Own Key' (BYOK) model storing tokens in `localStorage` securely fetched from users, or proxy requests through a secure backend server that manages the API keys.

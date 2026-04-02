# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded 3rd-Party API Keys
**Vulnerability:** A Hugging Face API token was hardcoded into the client-side JavaScript (`script.js`), split across two strings (`keyP1`, `keyP2`) to evade simple regex scanners, and sent directly to the Hugging Face Inference API from the browser.
**Learning:** Concatenating secrets in client-side code provides zero security against determined attackers who can simply read the resulting value in network requests or use browser developer tools.
**Prevention:** External API authentication for users must never be hardcoded on the client. Adopt a "Bring Your Own Key" (BYOK) model storing tokens in `localStorage` securely or proxy requests through a secure backend server that holds the secret key.

# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded Client-Side API Keys
**Vulnerability:** Hugging Face API keys (`keyP1`, `keyP2`, `HF_TOKEN`) were hardcoded directly in client-side JavaScript (`script.js`). Anyone inspecting the page source could extract the keys and use them, potentially leading to unauthorized access and quota exhaustion.
**Learning:** Client-side code is inherently untrusted. Splitting keys into parts does not provide security against even casual inspection.
**Prevention:** Migrate to a Bring-Your-Own-Key (BYOK) architecture where users provide their own tokens stored in `localStorage`, or implement a secure backend proxy that securely holds the keys and validates user requests before forwarding them to the external API.

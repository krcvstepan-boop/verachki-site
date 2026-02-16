# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2026-02-16 - Hardcoded API Key Exposure
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js` as a global constant, split into two strings to obfuscate it. Client-side obfuscation is not security; the key was visible to anyone inspecting the source.
**Learning:** Client-side applications cannot securely store secrets. Any "secret" in the frontend code is public.
**Prevention:** Implement a "Bring Your Own Key" (BYOK) model where the user provides the key (stored in `localStorage`) or proxy requests through a secure backend that holds the key.

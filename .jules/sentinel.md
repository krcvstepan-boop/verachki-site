# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-22 - Hardcoded API Key Exposure
**Vulnerability:** A Hugging Face API key was hardcoded in `script.js` as `const keyP1 = ...; const keyP2 = ...; const HF_TOKEN = keyP1 + keyP2;`. This exposed the key to anyone inspecting the source code.
**Learning:** Obfuscation by splitting strings does not prevent exposure in client-side code. Secrets in client-side code are inherently public.
**Prevention:** Use a "Bring Your Own Key" (BYOK) model for client-side AI features, storing the user's key in `localStorage` or `sessionStorage` and never committing it to the repo. Or use a backend proxy.

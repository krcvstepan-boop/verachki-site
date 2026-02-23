# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-22 - Hardcoded API Key (Hugging Face)
**Vulnerability:** The Hugging Face API token (`HF_TOKEN`) was split into two parts and concatenated in `script.js` to obfuscate it, but it was still hardcoded in client-side code, exposing the quota/billing to public misuse.
**Learning:** Client-side obfuscation is not security. Any secret in the frontend bundle is public.
**Prevention:** Implemented "Bring Your Own Key" (BYOK) pattern. The app now checks `localStorage` for the token. If missing, it prompts the user (only during interactive calls) to provide their own key, which is then stored locally. This shifts the cost/quota responsibility to the user and keeps the app secret-free.

# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-06-15 - Hardcoded API Key Exposure
**Vulnerability:** The Hugging Face API key (`HF_TOKEN`) was hardcoded in the frontend JavaScript codebase (`script.js`), exposing it to any user inspecting the site's source code.
**Learning:** Hardcoding secrets directly in client-side code makes them visible to the public. If an API key is exposed, malicious actors can use it, leading to financial loss or compromised services.
**Prevention:** Never store sensitive keys or tokens in frontend code. Use a 'Bring Your Own Key' (BYOK) model, fetching secrets from user input (like `localStorage`), or proxy external API requests through a secure backend that holds the secret.

# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded 3rd-Party API Keys in Client-Side JS
**Vulnerability:** External API authentication tokens (like Hugging Face `HF_TOKEN`) were hardcoded and concatenated within client-side JavaScript (`script.js`). This allowed anyone inspecting the source to extract and misuse the token for unauthorized AI API access, incurring costs or rate limits for the token owner.
**Learning:** Concatenating strings (`const HF_TOKEN = keyP1 + keyP2`) provides absolutely zero security against extraction. Client-side applications inherently expose all logic and variables to the user.
**Prevention:** 3rd-party API keys must never be hardcoded in frontend code. Use a Bring Your Own Key (BYOK) model storing tokens in `localStorage`, or proxy requests through a secure backend that holds the secret.

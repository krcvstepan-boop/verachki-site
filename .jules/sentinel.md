# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - [CRITICAL] Client-Side Hardcoded Secrets
**Vulnerability:** Hardcoded Hugging Face API tokens were present in , allowing anyone to extract and misuse the quota.
**Learning:** Client-side applications without a backend proxy cannot securely store API keys.
**Prevention:** Adopted a 'Bring Your Own Key' (BYOK) model. Implemented  and  to allow users to store their own keys in .

## 2024-05-23 - [CRITICAL] Client-Side Hardcoded Secrets
**Vulnerability:** Hardcoded Hugging Face API tokens were present in `script.js`, allowing anyone to extract and misuse the quota.
**Learning:** Client-side applications without a backend proxy cannot securely store API keys.
**Prevention:** Adopted a 'Bring Your Own Key' (BYOK) model. Implemented `getHFToken` and `setAIToken` to allow users to store their own keys in `localStorage`.

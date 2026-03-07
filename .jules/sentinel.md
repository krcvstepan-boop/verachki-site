# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2026-03-07 - Hardcoded API Keys in Client-Side JS
**Vulnerability:** A third-party API key (Hugging Face `HF_TOKEN`) was hardcoded into the client-side JavaScript (`script.js`) by splitting it across multiple variables (`keyP1`, `keyP2`). This allows anyone inspecting the source code or network requests to extract and misuse the token.
**Learning:** Obfuscating keys via string concatenation does not secure them on the client-side. All client-sent code is public.
**Prevention:** Implement a Bring Your Own Key (BYOK) system where the user provides their own token, which is stored locally (e.g., `localStorage`), or securely proxy API requests through a backend server.

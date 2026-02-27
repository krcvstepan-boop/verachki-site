# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2025-02-14 - Hardcoded API Secrets in Client-Side Code
**Vulnerability:** The Hugging Face API token (`HF_TOKEN`) was hardcoded directly in `script.js` as global constants (`keyP1` + `keyP2`). This exposed the secret to anyone viewing the source code, allowing potential quota theft or malicious API usage.
**Learning:** Splitting strings (e.g., `part1 + part2`) does not protect secrets in client-side JavaScript. Obfuscation is not security. Client-side apps cannot safely store secrets for backend services unless those services support restricted public keys (like Firebase/Appwrite).
**Prevention:** Implemented a "Bring Your Own Key" (BYOK) flow. The app now checks `localStorage` for the token. If missing, it prompts the user to enter their own. If the API returns a 401 Unauthorized, the token is automatically cleared, prompting the user again on the next interaction. This shifts the secret management responsibility to the user and avoids baking secrets into the repo.

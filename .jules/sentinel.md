# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-24 - Hardcoded AI API Tokens
**Vulnerability:** A Hugging Face API token was hardcoded in `script.js` (split into two parts to avoid simple grep). This allows anyone with access to the source code to use the developer's quota.
**Learning:** Obfuscation (splitting strings) is not security. Client-side applications cannot securely store global secrets.
**Prevention:** Implement "Bring Your Own Key" (BYOK) flows. Store user-provided keys in `localStorage` and prompt for them only during interactive sessions to maintain a smooth background experience.

## 2026-05-24 - IDOR and Missing Authorization in Client-Side Updates
**Vulnerability:** The application relied on `state.currentProfileId` (which could be set to any user's ID by clicking their profile) to perform updates in `saveMyProfile`. Additionally, `saveProfileChanges` (rank updates) lacked client-side checks for admin status.
**Learning:** Trusting client-side state that can be mutated by UI interactions for sensitive database operations leads to Insecure Direct Object Reference (IDOR) vulnerabilities.
**Prevention:** Always use the authenticated user's own profile ID (e.g., `state.profile.$id`) for self-service updates and implement explicit authorization checks (e.g., `ADMIN_EMAIL` check) before allowing sensitive operations, even on the frontend.

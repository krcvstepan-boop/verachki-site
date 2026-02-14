# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-18 - Client-Side API Key Pattern
**Vulnerability:** Hardcoded external API keys (Hugging Face) found in client-side JS.
**Learning:** This codebase relies on client-side logic for external services due to its static nature, making secret management difficult.
**Prevention:** Implemented a 'Bring Your Own Key' pattern using `localStorage` and `window.prompt` for interactive features, allowing security without backend infrastructure.

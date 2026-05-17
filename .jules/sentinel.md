# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2026-05-17 - Persistent XSS in Network Graph Tooltips
**Vulnerability:** Stored XSS in `network.js` where `node.name` (fetched from Appwrite) was injected directly into the HTML returned by the `nodeLabel` callback.
**Learning:** External libraries like `3d-force-graph` that accept HTML strings for tooltips bypass standard framework protections. Regressions occur when utility functions like `escapeHtml` are not shared or included in peripheral script files.
**Prevention:** Always sanitize dynamic data in graph tooltips. Centralize security utilities or ensure every script file that handles external data has access to sanitization functions.

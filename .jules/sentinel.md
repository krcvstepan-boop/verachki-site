# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Variable Shadowing in Global Functions
**Vulnerability:** While fixing a hardcoded API key by introducing `window.prompt`, the function argument was named `prompt`, shadowing the global `prompt`. This caused `TypeError: prompt is not a function` when trying to call the global prompt.
**Learning:** When refactoring code to use global browser APIs (like `prompt`, `name`, `status`), ensure local variable names do not shadow them, especially in older codebases where functions are in the global scope.
**Prevention:** Use explicit `window.prompt` to disambiguate, or rename local variables to be more descriptive (e.g., `userPrompt`).

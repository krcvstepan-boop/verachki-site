# Sentinel Journal

## 2024-05-22 - XSS in HTML Event Handlers and Templates
**Vulnerability:** User inputs (username, messages) were injected directly into inline event handlers (e.g., `onclick="func('${val}')"`) and template literals. Standard HTML escaping (`&`, `<`, `>`) is insufficient here because browsers decode HTML entities in attributes *before* JS parsing.
**Learning:** `escapeHtml` protects HTML content, but protecting JS strings inside HTML attributes requires escaping JS syntax characters (`'`, `"`, `` ` ``, `\`, `newline`).
**Prevention:** Use a dedicated `escapeJs` function for values injected into JS strings within HTML attributes. Better yet, avoid inline event handlers and use `addEventListener` where possible (though inline was kept here for minimal refactoring).

## 2024-05-23 - Hardcoded Client-Side API Keys
**Vulnerability:** The Hugging Face API token used for the AI system was hardcoded in `script.js` directly as string concatenation (`keyP1 + keyP2`). This is inherently insecure because client-side JS is accessible to everyone, meaning the token could easily be extracted and abused.
**Learning:** Never put sensitive tokens in client-side code, regardless of obfuscation via string splitting.
**Prevention:** Using a BYOK (Bring Your Own Key) model is necessary where the client is completely serverless or relies solely on third-party APIs from the browser. Using `localStorage` combined with `window.prompt` avoids embedding the token in the code itself, while cleanly requesting it only when required.

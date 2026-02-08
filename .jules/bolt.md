## 2026-02-08 - [Optimizing Render Loops]
**Learning:** `document.querySelectorAll` inside a `requestAnimationFrame` loop (60fps) is a major performance anti-pattern because it forces a full DOM traversal every frame. This scales poorly with the number of DOM nodes.
**Action:** Instead, cache a live `HTMLCollection` using `getElementsByClassName` or `getElementsByTagName` during initialization. This collection automatically stays in sync with DOM changes (like new chat messages), eliminating the need for re-querying, while providing O(1) access to the list reference.

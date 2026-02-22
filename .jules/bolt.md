## 2024-05-23 - DOM Query in Render Loop Optimization
**Learning:** `document.querySelectorAll` inside a `requestAnimationFrame` loop is a massive performance killer, forcing layout recalculations every frame.
**Action:** Replace with `IntersectionObserver` maintaining a `Set` of visible elements. Use `MutationObserver` to track added/removed nodes to keep the Set consistent without polling.

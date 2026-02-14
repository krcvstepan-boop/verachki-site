## 2024-05-24 - Optimization of 3D List Rendering
**Learning:** Polling `document.querySelectorAll` inside a 60fps animation loop (e.g., `requestAnimationFrame`) to find render targets causes severe style recalculation and DOM thrashing, especially when combined with `getBoundingClientRect`.
**Action:** Use `IntersectionObserver` to maintain a `Set` of visible elements. Iterate over this Set in the animation loop. This reduces complexity from O(Total Elements) to O(Visible Elements) and eliminates redundant DOM queries. Use `MutationObserver` to automatically track dynamically added elements.

## 2024-05-14 - Optimize render loop DOM queries
**Learning:** High-frequency render loops (`requestAnimationFrame`) suffer significant performance penalties when using `document.querySelectorAll` because it returns a static NodeList, forcing the browser to perform a full document traversal each frame. Additionally, repeatedly accessing layout properties like `window.innerHeight` can trigger layout thrashing.
**Action:** Always prefer `document.getElementsByClassName` for live HTMLCollections in tight loops, and cache static layout properties (like `window.innerHeight` and array lengths) outside the loop to minimize redundant overhead.

## 2024-05-14 - Use IntersectionObserver to prune high-frequency render loops
**Learning:** High-frequency render loops that interact with DOM elements (e.g., rendering Three.js scenes onto a single canvas spanning multiple DOM placeholders) should use `IntersectionObserver` to track visibility. Iterating through all placeholders and calling `getBoundingClientRect()` every frame to check visibility manually causes significant layout thrashing (O(N) complexity).
**Action:** Implement `IntersectionObserver` to maintain a `Set` of visible elements and only iterate over this `Set` in the `requestAnimationFrame` loop. This reduces layout-triggering calls from O(Total) to O(Visible), which often results in a 90%+ reduction in overhead for long lists.

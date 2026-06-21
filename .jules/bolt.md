## 2024-05-14 - Optimize render loop DOM queries
**Learning:** High-frequency render loops (`requestAnimationFrame`) suffer significant performance penalties when using `document.querySelectorAll` because it returns a static NodeList, forcing the browser to perform a full document traversal each frame. Additionally, repeatedly accessing layout properties like `window.innerHeight` can trigger layout thrashing.
**Action:** Always prefer `document.getElementsByClassName` for live HTMLCollections in tight loops, and cache static layout properties (like `window.innerHeight` and array lengths) outside the loop to minimize redundant overhead.

## 2026-06-21 - Visibility-driven render loop optimization
**Learning:** For scrollable lists with many independent 3D elements (like message avatars), even O(N) optimized DOM queries like `getElementsByClassName` combined with `getBoundingClientRect` become a bottleneck as N grows. Using `IntersectionObserver` to maintain a `Set` of visible elements reduces loop complexity to O(Visible), and `MutationObserver` ensures automatic registration of dynamic content.
**Action:** Implement `IntersectionObserver` tracking for any high-frequency render loop targeting multiple DOM elements to eliminate unnecessary layout-triggering calls for off-screen components.

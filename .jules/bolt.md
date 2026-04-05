## 2024-05-14 - Optimize render loop DOM queries
**Learning:** High-frequency render loops (`requestAnimationFrame`) suffer significant performance penalties when using `document.querySelectorAll` because it returns a static NodeList, forcing the browser to perform a full document traversal each frame. Additionally, repeatedly accessing layout properties like `window.innerHeight` can trigger layout thrashing.
**Action:** Always prefer `document.getElementsByClassName` for live HTMLCollections in tight loops, and cache static layout properties (like `window.innerHeight` and array lengths) outside the loop to minimize redundant overhead.

## 2026-04-05 - IntersectionObserver for Render Pruning
**Learning:** In applications with long lists of animated elements (like message avatars in a chat), per-frame `getBoundingClientRect()` calls for every element in the DOM (even if off-screen) quickly become a major performance bottleneck due to layout-triggering overhead.
**Action:** Use `IntersectionObserver` to maintain a set of currently visible elements. Prune the animation loop to iterate only over this set, significantly reducing the number of layout calculations and `traverse()` calls per frame. Caching material-heavy children (e.g., petals in Three.js) further eliminates the overhead of recursive traversal.

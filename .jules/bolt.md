## 2024-05-14 - Optimize render loop DOM queries
**Learning:** High-frequency render loops (`requestAnimationFrame`) suffer significant performance penalties when using `document.querySelectorAll` because it returns a static NodeList, forcing the browser to perform a full document traversal each frame. Additionally, repeatedly accessing layout properties like `window.innerHeight` can trigger layout thrashing.
**Action:** Always prefer `document.getElementsByClassName` for live HTMLCollections in tight loops, and cache static layout properties (like `window.innerHeight` and array lengths) outside the loop to minimize redundant overhead.

## 2024-05-15 - Optimize AvatarSystem with Visibility-Based Rendering
**Learning:** High-frequency 3D render loops that iterate over all DOM-associated elements (e.g., avatar placeholders in a chat) become a major bottleneck as the list grows (O(N)), primarily due to repeated layout-triggering calls like `getBoundingClientRect`.
**Action:** Use an `IntersectionObserver` to track visible elements in a `Set` and only process those in the render loop (O(Visible)). Combine with a `MutationObserver` for automatic registration of dynamic elements.

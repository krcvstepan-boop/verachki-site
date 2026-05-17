## 2024-05-14 - Optimize render loop DOM queries
**Learning:** High-frequency render loops (`requestAnimationFrame`) suffer significant performance penalties when using `document.querySelectorAll` because it returns a static NodeList, forcing the browser to perform a full document traversal each frame. Additionally, repeatedly accessing layout properties like `window.innerHeight` can trigger layout thrashing.
**Action:** Always prefer `document.getElementsByClassName` for live HTMLCollections in tight loops, and cache static layout properties (like `window.innerHeight` and array lengths) outside the loop to minimize redundant overhead.

## 2024-05-17 - Decouple visibility from render loops with IntersectionObserver
**Learning:** Even with `getElementsByClassName`, an O(N) loop that calls `getBoundingClientRect` remains a bottleneck as N grows. In chat applications with large message histories, this triggers layout thrashing every frame.
**Action:** Use `IntersectionObserver` to maintain a Set of visible elements and only process those in the render loop. Combined with `MutationObserver`, this creates a zero-maintenance O(Visible) system that drastically reduces CPU overhead.

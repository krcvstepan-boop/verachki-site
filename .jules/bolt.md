## 2024-05-14 - Optimize render loop DOM queries
**Learning:** High-frequency render loops (`requestAnimationFrame`) suffer significant performance penalties when using `document.querySelectorAll` because it returns a static NodeList, forcing the browser to perform a full document traversal each frame. Additionally, repeatedly accessing layout properties like `window.innerHeight` can trigger layout thrashing.
**Action:** Always prefer `document.getElementsByClassName` for live HTMLCollections in tight loops, and cache static layout properties (like `window.innerHeight` and array lengths) outside the loop to minimize redundant overhead.

## 2026-04-26 - Optimize 3D Avatar Render Loop with Viewport Culling
**Learning:** In applications with many 3D elements rendered over HTML placeholders (like chat avatars), iterating through all elements and calling `getBoundingClientRect()` every frame causes O(N) layout thrashing. Using `IntersectionObserver` to track visible nodes reduces the complexity to O(M) where M is the number of visible elements.
**Action:** Use `IntersectionObserver` with a `rootMargin` (e.g., '100px') to manage a `Set` of visible nodes for the render loop. Combine with `MutationObserver` for automatic tracking of dynamically added elements. Also, cache shader uniforms to avoid `group.traverse()` in high-frequency loops.

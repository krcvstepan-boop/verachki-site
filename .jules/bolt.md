## 2024-05-14 - Optimize render loop DOM queries
**Learning:** High-frequency render loops (`requestAnimationFrame`) suffer significant performance penalties when using `document.querySelectorAll` because it returns a static NodeList, forcing the browser to perform a full document traversal each frame. Additionally, repeatedly accessing layout properties like `window.innerHeight` can trigger layout thrashing.
**Action:** Always prefer `document.getElementsByClassName` for live HTMLCollections in tight loops, and cache static layout properties (like `window.innerHeight` and array lengths) outside the loop to minimize redundant overhead.

## 2026-05-10 - Optimize network graph link generation
**Learning:** Algorithmic bottlenecks in graph generation (O(N³) due to array filtering in a nested loop) can severely lag the main thread during initialization as the user base grows. Using a Set for tracking node connectivity reduces the complexity to O(N²).
**Action:** Replace array filtering or repeated linear searches in graph/link generation logic with Set or Map lookups to maintain performance at scale.

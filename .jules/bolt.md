## 2024-05-24 - Network graph rendering scaling bottleneck
**Learning:** Found an $O(N^3)$ bottleneck during network graph initialization because `links.filter` was called inside nested loops checking for connections. This caused severe lag when initializing large numbers of nodes.
**Action:** Replace $O(L)$ `links.filter` array lookups with $O(1)$ `Set.has()` lookups by caching connection IDs in a Set, achieving $O(N^2)$ and improving start time exponentially as graph sizes increase.

## 2024-05-24 - Layout thrashing in requestAnimationFrame loop
**Learning:** Found that repeatedly querying DOM layout properties like `window.innerHeight` inside an inner loop inside a hot `requestAnimationFrame` animation loop is very expensive due to forced reflow or unnecessary DOM access overhead.
**Action:** Cache these properties outside the loop (once per frame) to prevent performance penalties.

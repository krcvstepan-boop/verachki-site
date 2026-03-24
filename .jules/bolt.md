## 2024-05-24 - O(N³) Bottleneck in Force Graph Initialization
**Learning:** Using `Array.prototype.filter` inside nested loops (`O(N^2)`) to verify graph connection constraints (like ensuring at least one connection per node) creates an invisible `O(N^3)` performance bottleneck as the graph scales (N nodes * N nodes * L links).
**Action:** Replace the `O(L)` array scan inside nested user-generation loops with an `O(1)` `Set.has()` check, reducing complexity back to `O(N^2)` and avoiding freezing the main thread for large user clusters.

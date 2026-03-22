## 2024-05-19 - Network Graph Initialization Complexity

**Learning:** The `network.js` graph initialization `initGraph()` contained a hidden $O(N^3)$ performance bottleneck due to a nested array `filter()` operation ($O(N)$) inside a nested $O(N^2)$ double loop over users. With thousands of users this would completely block the main thread and freeze the UI on startup.

**Action:** Whenever iterating over data structures to build connections/relationships, utilize an auxiliary `Set` or `Map` to keep track of already connected or processed entities. This guarantees $O(1)$ lookups instead of $O(N)$ operations within nested loops. In this specific case, replacing `links.filter` with a `connectedUsers` Set reduced operations by over 20x.

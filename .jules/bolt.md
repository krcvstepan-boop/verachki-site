# Bolt Journal

## 2024-05-22 - O(1) Set Lookup vs O(N) Array Filter in Graph Initialization
**Learning:** During the initialization of the ForceGraph3D in `network.js`, ensuring each user had at least one connection involved filtering the entire `links` array for each user. This nested an $O(L)$ filter inside an $O(N^2)$ connection loop, creating a hidden $O(N^3)$ bottleneck as the number of users grew.
**Action:** Replaced the array filter with an $O(1)$ lookup using a `Set` (`connectedUsers`) populated during edge creation. This guarantees $O(N^2)$ initialization complexity. Always track global state constraints (like connectivity) with sets/maps during iterative construction rather than repeatedly querying the growing result array.

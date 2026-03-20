## 2024-03-20 - O(N³) to O(N²) in network.js graph generation
**Learning:** Checking for existing connections inside nested loops using `Array.prototype.filter()` over all edges creates an O(N³) complexity bottleneck during initial graph setup, specifically in `network.js` where `links.filter` is called for every user connection check.
**Action:** Replace `Array.prototype.filter()` on links with a dedicated O(1) `Set` (`connectedUsers`) tracking node IDs to ensure initialization stays O(N²).

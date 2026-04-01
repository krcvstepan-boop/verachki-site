## 2024-05-24 - [Avoid Array.filter inside nested loops]
**Learning:** Using `Array.prototype.filter()` inside an $O(N^2)$ nested loop (e.g., in `network.js` for graph links) introduces an invisible $O(L)$ multiplier, creating $O(N^3)$ complexity.
**Action:** Always use a `Set` or `Map` to track states (like `connectedUsers`) for $O(1)$ lookups instead of filtering arrays inside tight loops.

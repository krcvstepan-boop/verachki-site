## 2025-03-10 - Network Graph Initialization Complexity
**Learning:** In `network.js`, the `initGraph` algorithm was generating connections in an $O(N^3)$ manner due to repeatedly checking connection existence using an $O(L)$ `links.filter` call inside an $O(N^2)$ nested loop structure. As user bases scale, this array search severely bloats initial network graph load time.
**Action:** Always utilize a `Set` or `Map` to cache states like 'connected IDs' instead of re-iterating through growing unstructured arrays to verify relationships.

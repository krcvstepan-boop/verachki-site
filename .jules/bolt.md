## 2024-03-16 - O(1) Set Lookup Reduces Graph Initialization Complexity
**Learning:** In `network.js`, the network graph generation was checking for existing connections inside a nested loop by filtering an entire array of links (`links.filter()`), resulting in $O(N^3)$ complexity (where $N$ is users and $L$ is links, and $L \approx N^2$). This causes slow initialization times for large numbers of users.
**Action:** By maintaining an $O(1)$ `Set` of connected user IDs during graph generation, the complexity can be reduced to $O(N^2)$, dramatically improving initialization performance.

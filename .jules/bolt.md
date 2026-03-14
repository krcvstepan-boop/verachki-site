## 2024-05-24 - Network graph generation complexity
**Learning:** The graph generation in `network.js` uses an $O(N)$ filter inside an $O(N^2)$ double loop to check if a user is connected, leading to $O(N^3)$ initialization complexity.
**Action:** Replace the `links.filter` call with a `Set` to track connected users. This makes the check $O(1)$ and reduces initialization complexity to $O(N^2)$.

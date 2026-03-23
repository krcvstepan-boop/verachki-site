## 2024-05-24 - Network graph complexity optimization
**Learning:** In `network.js`, constructing the graph links initially had an $O(N^3)$ complexity because for every user, the code iterated over all previously created links using `links.filter` to check if a connection existed.
**Action:** Use a `Set` to keep track of connections during creation instead of re-iterating through the link array for $O(1)$ lookups and an overall $O(N^2)$ initialization performance.

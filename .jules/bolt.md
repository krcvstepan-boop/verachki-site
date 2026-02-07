## 2024-05-23 - DOM Query Optimization in Animation Loops
**Learning:** `document.querySelectorAll` is static and O(N), making it very expensive for high-frequency animation loops (60fps). `getElementsByClassName` returns a live `HTMLCollection` that automatically reflects DOM changes without re-querying.
**Action:** For animation loops tracking DOM elements, cache a `getElementsByClassName` collection during initialization instead of querying every frame.

## 2024-05-23 - Memory Integrity
**Learning:** Memory entries can be outdated or incorrect (e.g., claiming an optimization exists when it doesn't).
**Action:** Always verify the actual code state against memory claims before assuming an optimization is present.

## 2024-05-23 - Render Loop Dom Query Optimization
**Learning:** `querySelectorAll` and `getBoundingClientRect` called every frame in a render loop causes severe layout thrashing (O(N) * FPS), especially on mobile.
**Action:** Replace with `IntersectionObserver` to maintain a Set of visible elements, and only query layout properties for those elements. Use `MutationObserver` to track DOM changes.

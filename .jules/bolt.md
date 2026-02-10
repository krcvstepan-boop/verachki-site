## 2024-05-23 - Layout Thrashing in Animation Loops
**Learning:** Calling `getBoundingClientRect()` inside a `requestAnimationFrame` loop for every element (O(N)) causes severe layout thrashing and performance degradation.
**Action:** Use `IntersectionObserver` to maintain a set of visible elements and only process those in the render loop (O(visible)).

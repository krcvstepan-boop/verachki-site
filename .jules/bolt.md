## 2024-05-01 - DOM querying inside animation loops
**Learning:** Querying the DOM inside an animation loop (`requestAnimationFrame`) is an $O(N)$ operation that causes performance bottlenecks and layout thrashing as the number of elements grows.
**Action:** Replace DOM querying inside animation loops with an $O(M)$ operation over a `visibleAvatars` Set, managed via `IntersectionObserver` and `MutationObserver`.

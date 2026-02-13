## 2024-05-23 - 3D Rendering Optimization
**Learning:** In applications mixing DOM elements with WebGL overlays (like 3D avatars over chat messages), using `getBoundingClientRect()` inside the animation loop is a major performance bottleneck (O(N) layout thrashing).
**Action:** Use `IntersectionObserver` to maintain a set of visible elements (`visibleAvatars`). Iterate only over this set in the `animate` loop. This reduces complexity from O(Total) to O(Visible). Ensure `MutationObserver` is used to track dynamically added elements.

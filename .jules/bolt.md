
## 2024-05-15 - [avatar.js Render Loop Optimization]
**Learning:** Calling DOM-querying methods like `document.querySelectorAll` within the heavily-called `requestAnimationFrame` loop (used in WebGL animations) introduces measurable jitter and limits performance, especially as message history grows (O(N) operation).
**Action:** Implemented a combination of `MutationObserver` (to track when avatars are added/removed from the DOM) and `IntersectionObserver` (to track which are actively in the viewport). The render loop now just iterates over a pre-populated Set of `visibleAvatars`, converting the O(N) DOM query to an O(M) Set iteration.

## 2024-05-23 - Use IntersectionObserver for Animation Loop Visibility
**Learning:** The `SoulAvatarSystem`'s `animate` loop was performing `document.querySelectorAll` every frame, causing unnecessary DOM thrashing as the message list grows.
**Action:** When implementing animation loops that depend on DOM elements, always use `IntersectionObserver` to maintain a reactive set of visible elements instead of querying the DOM every frame.

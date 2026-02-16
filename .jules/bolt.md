## 2024-05-23 - Optimization of Render Loop via IntersectionObserver
**Learning:** In applications with long scrollable lists (like chat history) where each item triggers a complex render (e.g., 3D canvas overlay), querying the DOM (`querySelectorAll`) and calculating bounds (`getBoundingClientRect`) for every item in the animation loop is a massive bottleneck.
**Action:** Use `IntersectionObserver` to track visibility and maintain a `Set` of active elements. Iterate only this `Set` in the render loop. Use `MutationObserver` to attach the IO to new elements dynamically added to the list.

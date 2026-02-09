## 2024-05-23 - IntersectionObserver in Headless Tests
**Learning:** `IntersectionObserver` callbacks will NOT fire in Playwright (Chromium) if the observed element or its ancestors have `display: none`, even if you manually set dimensions and scroll positions on the container. The layout box must exist.
**Action:** When testing visibility logic, always ensure the container's parent hierarchy is visible (remove `.hidden` classes) in the test setup.

## 2024-05-23 - DOM Polling vs IntersectionObserver
**Learning:** Replacing `document.querySelectorAll` in a `requestAnimationFrame` loop with a `Set` managed by `IntersectionObserver` transforms the complexity from O(Total Elements) to O(Visible Elements).
**Action:** Always prefer `IntersectionObserver` for tracking visibility of list items in infinite scroll or chat applications to avoid layout thrashing (`getBoundingClientRect`) on off-screen elements.

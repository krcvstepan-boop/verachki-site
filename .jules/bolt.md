## 2024-10-27 - [Hidden SPA Elements Consume CPU]
**Learning:** Elements that are visually hidden (e.g., covered by other elements or off-screen) in an SPA but still exist in the DOM with active `requestAnimationFrame` loops will continue to consume CPU/GPU resources.
**Action:** Always pause animation loops (RAF/Intervals) when the associated component or view is not visible, using visibility state or navigation hooks.

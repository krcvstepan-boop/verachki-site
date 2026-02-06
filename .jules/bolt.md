## 2024-05-22 - [DOM Optimization]
**Learning:** `querySelectorAll` returns a static `NodeList` and forces a full DOM scan every time it's called. Inside a 60fps animation loop, this is a significant bottleneck as the DOM grows. `getElementsByClassName` returns a live `HTMLCollection` that updates automatically without rescanning, making it vastly superior for hot loops.
**Action:** Use `getElementsByClassName` or `getElementsByTagName` for collections accessed frequently in render loops.

## 2024-05-24 - High-Frequency DOM Query Optimization
**Learning:** In high-frequency execution paths like the `animate` loop in `avatar.js`, using `document.querySelectorAll` causes a full document traversal each frame, and querying `window.innerHeight` repeatedly causes layout thrashing.
**Action:** Use `document.getElementsByClassName` for faster, live HTMLCollections and cache layout properties like `window.innerHeight` and array lengths outside the loop to minimize overhead.

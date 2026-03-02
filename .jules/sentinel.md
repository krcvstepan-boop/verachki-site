## 2024-05-24 - Hardcoded Secrets Found
**Vulnerability:** Hugging Face API tokens (keyP1 and keyP2) are hardcoded in the frontend code.
**Learning:** Hardcoding secrets in the client side makes them visible to anyone examining the source code.
**Prevention:** Store secrets as environment variables, load them from a backend endpoint, or require the user to input them and store them in localStorage (BYOK flow).

def get_plan():
    print("""
1. Remove hardcoded HF_TOKEN from `script.js`.
2. Add a fallback mechanism using `localStorage` to get and store the HF_TOKEN.
3. Update `tryTriggerAI` and `askMistral` to use the dynamic token logic with proper prompting.
    """)

if __name__ == "__main__":
    get_plan()

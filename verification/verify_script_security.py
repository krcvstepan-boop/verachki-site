def verify_script():
    with open('script.js', 'r') as f:
        content = f.read()

    errors = []

    # 1. Check for Hardcoded Keys (Should be absent)
    if "hf_UwcAeGYbQKgyWa" in content:
        errors.append("CRITICAL: keyP1 found in script.js")
    if "AlccfNJwQoCAxVzHgSdS" in content:
        errors.append("CRITICAL: keyP2 found in script.js")
    if "const HF_TOKEN =" in content:
        errors.append("CRITICAL: HF_TOKEN constant still defined")

    # 2. Check for New Logic (Should be present)
    if "localStorage.getItem('HF_TOKEN')" not in content and 'localStorage.getItem("HF_TOKEN")' not in content:
        errors.append("ERROR: localStorage.getItem('HF_TOKEN') missing")

    if "window.prompt" not in content:
        errors.append("ERROR: window.prompt missing")

    if "localStorage.removeItem('HF_TOKEN')" not in content and 'localStorage.removeItem("HF_TOKEN")' not in content:
        errors.append("ERROR: localStorage.removeItem('HF_TOKEN') missing")

    if "askMistral(prompt, isDirectCall)" not in content:
        errors.append("ERROR: tryTriggerAI call to askMistral missing correct arguments")

    if errors:
        for e in errors:
            print(e)
        exit(1)
    else:
        print("SUCCESS: Script security verification passed.")

if __name__ == "__main__":
    verify_script()

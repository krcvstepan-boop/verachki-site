import re
import os
import subprocess

SCRIPT_PATH = 'script.js'
TEMP_JS_PATH = 'verification/temp_test.js'

def extract_function(content, func_name):
    pattern = re.compile(f'async function {func_name}\\s*\\(([^)]*)\\)\\s*{{')
    match = pattern.search(content)
    if not match:
        return None

    start_idx = match.start()
    open_braces = 0
    end_idx = -1

    for i in range(match.end() - 1, len(content)):
        if content[i] == '{':
            open_braces += 1
        elif content[i] == '}':
            open_braces -= 1
            if open_braces == 0:
                end_idx = i + 1
                break

    if end_idx == -1:
        return None

    return content[start_idx:end_idx]

def main():
    with open(SCRIPT_PATH, 'r', encoding='utf-8') as f:
        content = f.read()

    # 1. Static Analysis: Check for hardcoded secrets
    secrets = ['hf_UwcAeGYbQKgyWa', 'AlccfNJwQoCAxVzHgSdS', 'keyP1', 'keyP2']
    found_secrets = [s for s in secrets if s in content]

    if found_secrets:
        print(f"❌ FAILED: Found hardcoded secrets: {found_secrets}")
    else:
        print("✅ PASSED: No hardcoded secrets found.")

    # 2. Dynamic Analysis: Extract and Test askMistral
    func_code = extract_function(content, 'askMistral')
    if not func_code:
        print("❌ FAILED: Could not extract askMistral function.")
        return

    # Check signature
    if 'isInteractive' not in func_code and 'prompt' in func_code:
         # Initial check might fail if I haven't updated code yet, which is expected.
         print("⚠️ WARNING: askMistral signature does not seem to have isInteractive parameter yet (Expected for initial run).")

    # generate test harness
    js_test_code = f"""
// Mocks
const localStorage = {{
    store: {{}},
    getItem: function(key) {{ return this.store[key] || null; }},
    setItem: function(key, value) {{ this.store[key] = value; }},
    removeItem: function(key) {{ delete this.store[key]; }},
    clear: function() {{ this.store = {{}}; }}
}};

let promptCallCount = 0;
let lastPromptMsg = "";
const prompt = (msg) => {{
    promptCallCount++;
    lastPromptMsg = msg;
    return "test_token_from_prompt";
}};

const alert = (msg) => {{ console.log("Alert: " + msg); }};
const window = {{ prompt: prompt, alert: alert }};

// Mock Fetch
let fetchCallCount = 0;
let lastFetchHeaders = {{}};
const fetch = async (url, options) => {{
    fetchCallCount++;
    lastFetchHeaders = options.headers;
    if (options.headers.Authorization === 'Bearer invalid_token') {{
        return {{ ok: false, status: 401, json: async () => ({{}}) }};
    }}
    return {{
        ok: true,
        status: 200,
        json: async () => ([{{ generated_text: " AI Response" }}])
    }};
}};

// Extracted Function
{func_code}

// Tests
async function runTests() {{
    console.log("Running tests...");
    let passed = 0;
    let failed = 0;

    function assert(condition, msg) {{
        if (condition) {{
            // console.log("✅ " + msg);
            passed++;
        }} else {{
            console.error("❌ " + msg);
            failed++;
        }}
    }}

    // Test 1: No token, not interactive -> returns null, no prompt
    localStorage.clear();
    promptCallCount = 0;
    fetchCallCount = 0;

    // We need to handle the fact that the original function might not have isInteractive param yet.
    // Use call with 2 args anyway, JS allows it.
    let res = await askMistral("test", false);

    // If the code is NOT updated yet (original), it will try to fetch with HF_TOKEN global (which is missing here)
    // or fail because HF_TOKEN is not defined in this harness.
    // So we expect this to throw reference error for HF_TOKEN if using old code.

    // However, for the NEW code:
    assert(res === null, "Should return null if no token and not interactive");
    assert(promptCallCount === 0, "Should not prompt if not interactive");
    assert(fetchCallCount === 0, "Should not fetch if no token");

    // Test 2: No token, interactive -> prompts, saves, fetches
    localStorage.clear();
    promptCallCount = 0;
    fetchCallCount = 0;

    res = await askMistral("test", true);

    assert(promptCallCount === 1, "Should prompt if interactive");
    assert(localStorage.getItem('HF_TOKEN') === 'test_token_from_prompt', "Should save token");
    assert(fetchCallCount === 1, "Should fetch after getting token");
    assert(res === "AI Response", "Should return AI response");

    // Test 3: Has token -> uses it
    localStorage.setItem('HF_TOKEN', 'stored_token');
    promptCallCount = 0;
    fetchCallCount = 0;

    res = await askMistral("test", false);

    assert(promptCallCount === 0, "Should not prompt if token exists");
    assert(fetchCallCount === 1, "Should fetch");
    assert(lastFetchHeaders.Authorization === 'Bearer stored_token', "Should use stored token");

    // Test 4: 401 Error -> clears token
    localStorage.setItem('HF_TOKEN', 'invalid_token');
    fetchCallCount = 0;

    try {{
        await askMistral("test", false);
    }} catch(e) {{}}

    assert(localStorage.getItem('HF_TOKEN') === undefined || localStorage.getItem('HF_TOKEN') === null, "Should clear token on 401");

    console.log(`Tests finished: ${{passed}} passed, ${{failed}} failed.`);
    if (failed > 0) process.exit(1);
}}

runTests();
"""

    with open(TEMP_JS_PATH, 'w', encoding='utf-8') as f:
        f.write(js_test_code)

    try:
        result = subprocess.run(['node', TEMP_JS_PATH], capture_output=True, text=True)
        print(result.stdout)
        if result.returncode != 0:
            print("❌ Verification Failed:")
            print(result.stderr)
        else:
            print("✅ Logic Verification Passed")
    finally:
        if os.path.exists(TEMP_JS_PATH):
            os.remove(TEMP_JS_PATH)

if __name__ == "__main__":
    main()


// Mock Browser Environment
const localStorageMock = new Map();
const window = {
    prompt: (msg) => {
        console.log(`[Prompt]: ${msg}`);
        return "user_provided_token"; // Simulate user input
    },
    setAIToken: null // Will be defined by code
};

const localStorage = {
    getItem: (key) => localStorageMock.has(key) ? localStorageMock.get(key) : null,
    setItem: (key, val) => localStorageMock.set(key, val),
    removeItem: (key) => localStorageMock.delete(key)
};

// Mock Fetch
let fetchResponseStatus = 200;
let fetchResponseData = [{ generated_text: "AI Response" }];

async function fetch(url, options) {
    console.log(`[Fetch] URL: ${url}`);
    if (options && options.headers) {
         console.log(`[Fetch] Auth Header:`, options.headers.Authorization);
    }

    if (fetchResponseStatus === 401) {
        return {
            ok: false,
            status: 401,
            json: async () => ({ error: "Unauthorized" })
        };
    }

    return {
        ok: true,
        status: 200,
        json: async () => fetchResponseData
    };
}

// --- CODE UNDER TEST (Pasted from script.js) ---
window.setAIToken = function(token) {
    if (token) {
        localStorage.setItem('HF_TOKEN', token);
        console.log("AI Token updated.");
    } else {
        localStorage.removeItem('HF_TOKEN');
        console.log("AI Token cleared.");
    }
};

async function askMistral(prompt, isInteractive = false) {
    try {
        let token = localStorage.getItem('HF_TOKEN');

        if (!token) {
            if (isInteractive) {
                token = window.prompt("Введите Hugging Face Token (Read Access) для активации ИИ:");
                if (token) {
                    window.setAIToken(token);
                } else {
                    return null;
                }
            } else {
                console.warn("AI Token missing for background trigger.");
                return null;
            }
        }

        const systemPrompt = "Ты — СИСТЕМА, искусственный интеллект-наблюдатель чата 'Верачки'. Твой характер: ироничный, загадочный, киберпанковый. Ты не человек. Отвечай кратко (1-2 предложения).";

        const fullPrompt = `<s>[INST] ${systemPrompt} \n\nВходящие данные:\n${prompt} [/INST]`;

        const response = await fetch(
            "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json"
                },
                method: "POST",
                body: JSON.stringify({
                    inputs: fullPrompt,
                    parameters: { max_new_tokens: 100, return_full_text: false }
                }),
            }
        );

        if (response.status === 401) {
            console.error("AI Token Invalid. Clearing.");
            window.setAIToken(null);
            if (isInteractive) return askMistral(prompt, true); // Retry once
            return null;
        }

        if (!response.ok) throw new Error("AI Error");
        const result = await response.json();
        return result[0].generated_text.trim();
    } catch (error) {
        console.error(error);
        return null;
    }
}
// --- END CODE UNDER TEST ---

// TEST RUNNER
async function runTests() {
    console.log("=== TEST 1: Background Trigger, No Token ===");
    localStorageMock.clear();
    const res1 = await askMistral("Hello", false);
    if (res1 === null) console.log("PASS: Returns null silently.");
    else console.error("FAIL: Should return null");

    console.log("\n=== TEST 2: Interactive Trigger, No Token ===");
    localStorageMock.clear();
    const res2 = await askMistral("Hello", true);
    if (res2 === "AI Response" && localStorage.getItem('HF_TOKEN') === "user_provided_token") {
        console.log("PASS: Prompted, saved token, and fetched.");
    } else {
        console.error("FAIL: Did not handle interactive login correctly.");
    }

    console.log("\n=== TEST 3: Stored Token Usage ===");
    // Token is already set from Test 2
    const res3 = await askMistral("Hello", false);
    if (res3 === "AI Response") console.log("PASS: Used stored token.");
    else console.error("FAIL: Failed to use stored token.");

    console.log("\n=== TEST 4: Invalid Token Handling (401) ===");
    localStorage.setItem('HF_TOKEN', 'bad_token');
    fetchResponseStatus = 401;

    // We mock prompt to return NULL this time to break recursion
    window.prompt = () => null;

    const res4 = await askMistral("Hello", true);

    if (localStorage.getItem('HF_TOKEN') === null) {
        console.log("PASS: Token cleared on 401.");
    } else {
        console.error("FAIL: Token not cleared. Value: " + localStorage.getItem('HF_TOKEN'));
    }
}

runTests();

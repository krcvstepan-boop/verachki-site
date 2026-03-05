const fs = require('fs');

// Simple mock environment
global.window = {
    prompt: function(msg) {
        console.log("Mock prompt:", msg);
        return "mock_hf_token_123";
    },
    localStorage: {
        _data: {},
        setItem: function(id, val) { return this._data[id] = String(val); },
        getItem: function(id) { return this._data.hasOwnProperty(id) ? this._data[id] : null; },
        removeItem: function(id) { return delete this._data[id]; },
        clear: function() { return this._data = {}; }
    }
};
global.localStorage = global.window.localStorage;
global.fetch = async function(url, options) {
    if (url.includes('mistralai')) {
        console.log("Mock fetch to Mistral with headers:", options.headers);
        return {
            ok: true,
            status: 200,
            json: async () => [{ generated_text: "Mocked AI Response" }]
        };
    }
    return { ok: true, json: async () => ({}) };
};

global.document = {};
global.Appwrite = {
    Client: class { setEndpoint(){return this;} setProject(){return this;} },
    Account: class {},
    Databases: class {},
    Storage: class {},
    ID: { unique: () => 'id123' },
    Query: {}
};

// Evaluate the script (extract only askMistral logic for isolated testing to avoid DOM dependency)
const scriptContent = fs.readFileSync('script.js', 'utf8');

// Find askMistral function
const funcMatch = scriptContent.match(/async function askMistral\([\s\S]*?\n        \}/);
if (funcMatch) {
    eval(funcMatch[0]);

    // Run the test
    askMistral("Hello AI", true).then(res => {
        console.log("AI Response:", res);
        console.log("Token in localStorage:", global.localStorage.getItem('HF_TOKEN'));
        if (global.localStorage.getItem('HF_TOKEN') === "mock_hf_token_123") {
            console.log("VERIFICATION SUCCESS");
        } else {
            console.log("VERIFICATION FAILED");
        }
    }).catch(err => {
        console.error(err);
    });
} else {
    console.log("Could not find askMistral function");
}

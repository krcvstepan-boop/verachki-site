#!/bin/bash

# Define the secrets to search for
SECRET1="hf_UwcAeGYbQKgyWa"
SECRET2="AlccfNJwQoCAxVzHgSdS"
SECRET3="HF_TOKEN = keyP1 + keyP2"

echo "Scanning script.js for secrets..."

# Function to check for a secret
check_secret() {
    local secret="$1"
    if grep -qF "$secret" script.js; then
        echo "❌ FOUND SECRET: $secret"
        return 1
    else
        echo "✅ Secret not found: $secret"
        return 0
    fi
}

FAIL=0

check_secret "$SECRET1" || FAIL=1
check_secret "$SECRET2" || FAIL=1
check_secret "$SECRET3" || FAIL=1

if [ $FAIL -eq 0 ]; then
    echo "🎉 All secrets successfully removed!"
    exit 0
else
    echo "🚨 Some secrets still exist!"
    exit 1
fi

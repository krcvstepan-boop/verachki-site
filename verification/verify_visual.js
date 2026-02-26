const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');

(async () => {
    // 1. Setup Browser
    const browser = await chromium.launch({
        args: ['--no-sandbox', '--disable-setuid-sandbox', '--disable-web-security']
    });
    const context = await browser.newContext({
        viewport: { width: 1280, height: 720 },
        deviceScaleFactor: 1,
    });
    const page = await context.newPage();

    // 2. Mock Appwrite & Three.js to prevent errors and network calls
    await page.addInitScript(() => {
        window.Appwrite = {
            Client: class { setEndpoint() { return this; } setProject() { return this; } subscribe() {} },
            Account: class { get() { return Promise.resolve({ name: 'TestUser', email: 'test@example.com' }); } },
            Databases: class {
                listDocuments() { return Promise.resolve({ documents: [] }); }
                createDocument() { return Promise.resolve({}); }
                updateDocument() { return Promise.resolve({}); }
                deleteDocument() { return Promise.resolve({}); }
            },
            Storage: class { getFileView() { return ''; } },
            ID: { unique: () => 'unique_id' },
            Query: { orderAsc: () => {}, limit: () => {}, equal: () => {} }
        };
    });

    // 3. Load Page
    const filePath = path.resolve(__dirname, '../index.html');
    const fileUrl = 'file://' + filePath;
    console.log(`Loading: ${fileUrl}`);
    await page.goto(fileUrl, { waitUntil: 'domcontentloaded' });

    // 4. Inject Test Data (Simulate Chat with Avatars)
    await page.waitForTimeout(2000); // Allow scripts to load

    await page.evaluate(() => {
        // Force show interface
        document.getElementById('app-interface').classList.remove('hidden');
        document.getElementById('app-interface').style.display = 'block';

        const container = document.getElementById('messages-container');
        if (!container) return;

        container.innerHTML = '';

        // Add avatars
        for(let i=0; i<5; i++) {
            const row = document.createElement('div');
            row.className = 'message-row';
            row.style.height = '100px';
            row.style.width = '100%';
            row.style.display = 'flex';

            const avatar = document.createElement('div');
            avatar.className = 'soul-avatar-placeholder';
            avatar.dataset.user = `User${i}`;
            avatar.style.width = '50px';
            avatar.style.height = '50px';
            avatar.style.background = 'red'; // Visual debug
            avatar.style.border = '2px solid black';

            row.appendChild(avatar);
            container.appendChild(row);
        }

        // Initialize manually if needed
        if (window.AvatarSystem) {
             console.log("Initializing AvatarSystem manually...");
             window.AvatarSystem.init();
        }
    });

    // Wait for IntersectionObserver
    await page.waitForTimeout(2000);

    // 5. Verify Logic via Internal State
    const result = await page.evaluate(() => {
        const system = window.AvatarSystem;
        if (!system) return { error: "AvatarSystem not found" };

        const visibleCount = system.visibleAvatars ? system.visibleAvatars.size : -1;

        return {
            visibleCount,
            isRunning: system.isRunning,
            hasObserver: !!system.observer
        };
    });

    console.log('Verification State:', result);

    // 6. Screenshot for manual visual check
    await page.screenshot({ path: 'verification/avatar_verification.png', fullPage: true });
    console.log('Screenshot saved to verification/avatar_verification.png');

    await browser.close();

    if (result.visibleCount > 0 && result.hasObserver) {
        console.log('SUCCESS: Avatars are tracked via IntersectionObserver.');
        process.exit(0);
    } else {
        console.error('FAILURE: Avatar tracking failed.');
        process.exit(1);
    }
})();

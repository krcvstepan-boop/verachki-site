const fs = require('fs');

const users = [];
for (let i = 0; i < 100; i++) {
    users.push({ id: `user-${i}` });
}

function originalInit(users) {
    const links = [];
    let ops = 0;
    for (let i = 0; i < users.length; i++) {
        for (let j = i + 1; j < users.length; j++) {
            if (Math.random() < 0.3) {
                links.push({ source: users[i].id, target: users[j].id });
            }
            ops++;
        }
        const filterRes = links.filter(l => l.source === users[i].id || l.target === users[i].id);
        ops += links.length;
        if (users.length > 1 && filterRes.length === 0) {
            const target = users[(i + 1) % users.length];
            links.push({ source: users[i].id, target: target.id });
        }
    }
    return { links, ops };
}

function optimizedInit(users) {
    const links = [];
    const connectedUsers = new Set();
    let ops = 0;
    for (let i = 0; i < users.length; i++) {
        for (let j = i + 1; j < users.length; j++) {
            if (Math.random() < 0.3) {
                links.push({ source: users[i].id, target: users[j].id });
                connectedUsers.add(users[i].id);
                connectedUsers.add(users[j].id);
            }
            ops++;
        }
        ops += 1; // Set.has is O(1)
        if (users.length > 1 && !connectedUsers.has(users[i].id)) {
            const target = users[(i + 1) % users.length];
            links.push({ source: users[i].id, target: target.id });
            connectedUsers.add(users[i].id);
            connectedUsers.add(target.id);
        }
    }
    return { links, ops };
}

console.time('original');
let origOps = 0;
for (let i = 0; i < 100; i++) origOps = originalInit(users).ops;
console.timeEnd('original');

console.time('optimized');
let optOps = 0;
for (let i = 0; i < 100; i++) optOps = optimizedInit(users).ops;
console.timeEnd('optimized');

console.log("Original operations per call:", origOps);
console.log("Optimized operations per call:", optOps);

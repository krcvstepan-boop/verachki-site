// CONFIGURATION
const PROJECT_ID = '69624669002d880cd7bb';
const ENDPOINT = 'https://fra.cloud.appwrite.io/v1';
const DB_ID = '6962475a003af27425fb';
const PROFILES_COL = 'profiles';

// APPWRITE SETUP
const { Client, Databases, Query } = Appwrite;
const client = new Client().setEndpoint(ENDPOINT).setProject(PROJECT_ID);
const db = new Databases(client);

// SETTINGS
const IS_MOBILE = window.innerWidth < 768;
const PHANTOM_COUNT = IS_MOBILE ? 30 : 60;

async function fetchUsers() {
    try {
        const res = await db.listDocuments(DB_ID, PROFILES_COL, [Query.limit(100)]);
        return res.documents.map(doc => ({
            id: doc.username,
            name: doc.username,
            group: 'user',
            val: 10 // Size
        }));
    } catch (e) {
        console.error("Failed to fetch users", e);
        return [];
    }
}

function generatePhantoms() {
    const phantoms = [];
    for (let i = 0; i < PHANTOM_COUNT; i++) {
        phantoms.push({
            id: `phantom-${i}`,
            name: Math.random() > 0.5 ? "Сигнал Зашифрован" : "ID: Неизвестен",
            group: 'phantom',
            val: 3 // Size
        });
    }
    return phantoms;
}

async function initGraph() {
    const users = await fetchUsers();
    const phantoms = generatePhantoms();
    const nodes = [...users, ...phantoms];
    const links = [];

    // ⚡ Bolt: Use a Set to track connected users for O(1) lookups instead of O(N) array filtering
    const connectedUsers = new Set();

    // Connect users to form a core web
    for (let i = 0; i < users.length; i++) {
        for (let j = i + 1; j < users.length; j++) {
            // 30% chance to connect any two users
            if (Math.random() < 0.3) {
                links.push({ source: users[i].id, target: users[j].id });
                connectedUsers.add(users[i].id);
                connectedUsers.add(users[j].id);
            }
        }
        // Ensure at least one connection for each user if users exist
        if (users.length > 1 && !connectedUsers.has(users[i].id)) {
            const target = users[(i + 1) % users.length];
            links.push({ source: users[i].id, target: target.id });
            connectedUsers.add(users[i].id);
            connectedUsers.add(target.id);
        }
    }

    // Connect phantoms
    nodes.forEach(node => {
        if (node.group === 'phantom') {
            // Connect to a random user (attach to the core)
            if (users.length > 0) {
                const targetUser = users[Math.floor(Math.random() * users.length)];
                links.push({ source: node.id, target: targetUser.id });
            } else {
                // If no users, connect to random phantom
                const target = phantoms[Math.floor(Math.random() * phantoms.length)];
                if (target.id !== node.id) links.push({ source: node.id, target: target.id });
            }

            // Random extra connections
            if (Math.random() < 0.2) {
                 const target = phantoms[Math.floor(Math.random() * phantoms.length)];
                 if (target.id !== node.id) links.push({ source: node.id, target: target.id });
            }
        }
    });

    const graphData = { nodes, links };
    const elem = document.getElementById('graph-container');

    const Graph = ForceGraph3D()
        (elem)
        .graphData(graphData)
        .backgroundColor('#FFFFFF')
        .showNavInfo(false)
        .nodeLabel(node => {
            const color = node.group === 'user' ? '#00ffff' : '#888';
            const label = node.group === 'user' ? 'ГРАЖДАНИН' : 'НЕИЗВЕСТНО';
            return `<div style="text-align:center; color:${color}; font-weight:bold; font-family:'Courier New'; font-size:1.2em;">${node.name}</div><div style="font-size:0.8em; color:#ccc;">${label}</div>`;
        })
        .nodeThreeObject(node => {
            if (node.group === 'user') {
                const geometry = new THREE.SphereGeometry(node.val, 16, 16);
                const material = new THREE.MeshLambertMaterial({
                    color: 0x00ffff,
                    transparent: true,
                    opacity: 0.6
                });
                const mesh = new THREE.Mesh(geometry, material);
                return mesh;
            } else {
                const geometry = new THREE.SphereGeometry(node.val, 8, 8);
                const material = new THREE.MeshLambertMaterial({
                    color: 0x888888,
                    transparent: true,
                    opacity: 0.2
                });
                return new THREE.Mesh(geometry, material);
            }
        })
        .linkWidth(0.5)
        .linkColor(() => '#cccccc')
        .linkOpacity(0.3);

    // Initial camera orbit
    let angle = 0;
    const distance = 400;

    function animate() {
        if (document.hidden) {
            setTimeout(animate, 1000);
            return;
        }

        if (Graph) {
            angle += 0.001;
            Graph.cameraPosition({
                x: distance * Math.sin(angle),
                z: distance * Math.cos(angle)
            });
        }
        requestAnimationFrame(animate);
    }
    animate();

    // Resize handler
    window.addEventListener('resize', () => {
        Graph.width(window.innerWidth);
        Graph.height(window.innerHeight);
    });
}

initGraph();

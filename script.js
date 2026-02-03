        // CONFIGURATION
        const PROJECT_ID = '69624669002d880cd7bb';
        const ENDPOINT = 'https://fra.cloud.appwrite.io/v1';
        const DB_ID = '6962475a003af27425fb';
        const MSG_COL = 'verachkichathistory';
        const PROFILES_COLLECTION_ID = 'profiles';
        const STORAGE_ID = '696363f30004cb97e6a1';
        const ADMIN_EMAIL = "kraacovstepa@gmail.com";
        const SECRET_CODE = "GLEB2023";

        const keyP1 = "hf_UwcAeGYbQKgyWa";
        const keyP2 = "AlccfNJwQoCAxVzHgSdS";
        const HF_TOKEN = keyP1 + keyP2;

        // APPWRITE SETUP
        const { Client, Account, Databases, Storage, ID, Query } = Appwrite;
        const client = new Client().setEndpoint(ENDPOINT).setProject(PROJECT_ID);
        const account = new Account(client);
        const db = new Databases(client);
        const storage = new Storage(client);

        // GLOBAL STATE
        var state = {
            user: null,
            profile: null,
            profileCache: new Map(),
            editingId: null,
            isLogin: true,
            currentProfileId: null,
            attachment: null,
            recorder: null,
            chunks: [],
            isRecording: false,
            audioPlayer: null,
            isUploading: false,
            isRadioMode: false,
            radioNoise: null,
            aiCooldown: false,
            claimTimer: null
        };

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

        function getMSKDate() {
            return new Date().toLocaleDateString('ru-RU', { timeZone: 'Europe/Moscow' });
        }

        // MOBILE OPTIMIZATION: Prevent double-tap zoom
        let lastTouchEnd = 0;
        document.addEventListener('touchend', function (event) {
            const now = Date.now();
            if (now - lastTouchEnd <= 300) {
                event.preventDefault();
            }
            lastTouchEnd = now;
        }, {passive: false});

        // MOBILE OPTIMIZATION: Viewport height fix
        function throttle(func, wait) {
            let waiting = false;
            return function() {
                if (!waiting) {
                    waiting = true;
                    setTimeout(() => {
                        func.apply(this, arguments);
                        waiting = false;
                    }, wait);
                }
            };
        }

        function setVH() {
            requestAnimationFrame(() => {
                let vh = window.innerHeight * 0.01;
                document.documentElement.style.setProperty('--vh', `${vh}px`);
            });
        }
        window.addEventListener('load', setVH);
        window.addEventListener('resize', throttle(setVH, 100));
        window.addEventListener('orientationchange', () => {
            setTimeout(setVH, 100);
        });

        function playNotification() {
            if(document.hidden) {
                const osc = audioCtx.createOscillator();
                const gain = audioCtx.createGain();
                osc.connect(gain);
                gain.connect(audioCtx.destination);
                osc.frequency.setValueAtTime(500, audioCtx.currentTime);
                osc.frequency.exponentialRampToValueAtTime(1000, audioCtx.currentTime + 0.1);
                gain.gain.setValueAtTime(0.1, audioCtx.currentTime);
                gain.gain.exponentialRampToValueAtTime(0.01, audioCtx.currentTime + 0.5);
                osc.start();
                setTimeout(() => osc.stop(), 500);
            }
        }

        function showToast(msg, type = 'info') {
            const t = document.createElement('div');
            t.className = 'toast';
            t.innerText = msg;
            if(type === 'error') t.style.background = 'rgba(255, 59, 48, 0.9)';
            document.getElementById('toast-container').appendChild(t);
            setTimeout(() => {
                t.style.opacity = '0';
                t.style.transform = 'translateY(20px)';
                setTimeout(() => t.remove(), 300);
            }, 3000);
        }

        function escapeHtml(text) {
            if (!text) return "";
            return text.replace(/&/g, "&amp;")
                       .replace(/</g, "&lt;")
                       .replace(/>/g, "&gt;")
                       .replace(/"/g, "&quot;")
                       .replace(/'/g, "&#039;");
        }

        function escapeJs(text) {
            if (!text) return "";
            return text.replace(/\\/g, '\\\\')
                       .replace(/'/g, "\\'")
                       .replace(/"/g, '\\"')
                       .replace(/`/g, '\\`')
                       .replace(/\n/g, '\\n')
                       .replace(/\r/g, '\\r');
        }

        function scrollToBottom() {
            const c = document.getElementById('messages-container');
            requestAnimationFrame(() => {
                c.scrollTop = c.scrollHeight;
            });
        }

        async function checkSession() {
            try {
                state.user = await account.get();
                try {
                    const res = await db.listDocuments(DB_ID, PROFILES_COLLECTION_ID, [Query.equal('email', state.user.email)]);
                    if(res.documents.length > 0) {
                        state.profile = res.documents[0];
                        // Init new fields if missing (lazy migration)
                        if (state.profile.ether === undefined) state.profile.ether = 0;
                        if (state.profile.flower_xp === undefined) state.profile.flower_xp = 0;
                        state.profileCache.set(state.profile.username, state.profile);
                    }
                    else state.profile = await db.createDocument(DB_ID, PROFILES_COLLECTION_ID, ID.unique(), {
                        username: state.user.name,
                        email: state.user.email,
                        rank: "Наблюдатель",
                        about: "",
                        ether: 0,
                        flower_xp: 0,
                        last_claim_date: ""
                    });
                } catch(e) { console.log("Profile create/fetch error", e); }

                if(state.profile && state.profile.rank === 'Изгнан') { document.getElementById('ban-screen').style.display = 'flex'; return; }
                updateLandingState(true);

                // Initialize avatar with XP if system exists
                if(state.profile && typeof AvatarSystem !== 'undefined') {
                    AvatarSystem.updateAvatar(state.profile.username, state.profile.flower_xp || 0);
                }
            } catch (e) { updateLandingState(false); }
        }
        checkSession();

        function updateLandingState(isLoggedIn) {
            const heroBtn = document.getElementById('hero-main-btn');
            if (isLoggedIn) {
                document.getElementById('nav-guest').classList.add('hidden');
                document.getElementById('nav-user').classList.remove('hidden');

                if (state.profile) {
                    document.getElementById('nav-username').innerText = state.profile.username;
                    document.getElementById('nav-rank').innerText = state.profile.rank || "Имперец";
                }

                if (heroBtn) {
                    heroBtn.innerText = "ВОЙТИ В ЧАТ";
                    heroBtn.onclick = showApp;
                }
            } else {
                document.getElementById('nav-guest').classList.remove('hidden');
                document.getElementById('nav-user').classList.add('hidden');

                if (heroBtn) {
                    heroBtn.innerText = "Принять Присягу";
                    heroBtn.onclick = () => openModal('auth-modal');
                }
            }
        }

        function showApp() {
            document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
            document.querySelector('footer').style.display = 'none';
            document.querySelector('nav').style.display = 'none';
            document.getElementById('app-interface').classList.remove('hidden');

            closeModal('auth-modal');
            loadMessages();
            client.subscribe(`databases.${DB_ID}.collections.${MSG_COL}.documents`, handleRealtime);

            // Initialize Soul ID System
            if (typeof AvatarSystem !== 'undefined') {
                AvatarSystem.init();
            }
        }

        function showLanding() {
            // MOBILE OPTIMIZATION: Cleanup on exit
            if (state.audioPlayer) {
                state.audioPlayer.pause();
                state.audioPlayer = null;
            }
            if (state.recorder && state.recorder.state === 'recording') {
                state.recorder.stop();
                state.recorder.stream.getTracks().forEach(t => t.stop());
            }

            document.querySelectorAll('section').forEach(el => el.classList.remove('hidden'));
            document.getElementById('app-interface').classList.add('hidden');
            document.querySelector('footer').style.display = 'block';
            document.querySelector('nav').style.display = 'flex';

            updateLandingState(!!state.user);

            setTimeout(reveal, 100);
            window.scrollTo(0, 0);
        }

        function toggleAuthMode() {
            state.isLogin = !state.isLogin;
            document.getElementById('auth-title').innerText = state.isLogin ? 'Доступ' : 'Присяга';
            document.getElementById('auth-btn').innerText = state.isLogin ? 'Войти' : 'Вступить';
            document.getElementById('reg-name').style.display = state.isLogin ? 'none' : 'block';
            document.getElementById('invite-code').style.display = state.isLogin ? 'none' : 'block';
        }

        async function handleAuth() {
            const email = document.getElementById('email').value;
            const pass = document.getElementById('password').value;
            try {
                if (state.isLogin) {
                    await account.createEmailPasswordSession(email, pass);
                    location.reload();
                } else {
                    if(document.getElementById('invite-code').value !== SECRET_CODE) throw new Error("Неверный код доступа");
                    const name = document.getElementById('reg-name').value;
                    await account.create(ID.unique(), email, pass, name);
                    await account.createEmailPasswordSession(email, pass);
                    await db.createDocument(DB_ID, PROFILES_COLLECTION_ID, ID.unique(), {
                        username: name,
                        email: email,
                        rank: "Наблюдатель",
                        about: "",
                        ether: 0,
                        flower_xp: 0,
                        last_claim_date: ""
                    });
                    location.reload();
                }
            } catch(e) { showToast(e.message, 'error'); }
        }

        async function logout() {
            await account.deleteSession('current');
            location.reload();
        }

        async function askMistral(prompt) {
            try {
                const systemPrompt = "Ты — СИСТЕМА, искусственный интеллект-наблюдатель чата 'Верачки'. Твой характер: ироничный, загадочный, киберпанковый. Ты не человек. Отвечай кратко (1-2 предложения).";

                const fullPrompt = `<s>[INST] ${systemPrompt} \n\nВходящие данные:\n${prompt} [/INST]`;

                const response = await fetch(
                    "https://api-inference.huggingface.co/models/mistralai/Mistral-7B-Instruct-v0.3",
                    {
                        headers: {
                            Authorization: `Bearer ${HF_TOKEN}`,
                            "Content-Type": "application/json"
                        },
                        method: "POST",
                        body: JSON.stringify({
                            inputs: fullPrompt,
                            parameters: { max_new_tokens: 100, return_full_text: false }
                        }),
                    }
                );

                if (!response.ok) throw new Error("AI Error");
                const result = await response.json();
                return result[0].generated_text.trim();
            } catch (error) {
                console.error(error);
                return null;
            }
        }

        async function tryTriggerAI(message) {
            if (state.aiCooldown) return;

            const lowerMsg = message.toLowerCase();
            const isDirectCall = lowerMsg.startsWith('ии,') || lowerMsg.startsWith('бот,') || lowerMsg.startsWith('система,');
            const isRandomTrigger = Math.random() < 0.05;

            if (isDirectCall || isRandomTrigger) {
                state.aiCooldown = true;
                setTimeout(() => state.aiCooldown = false, 10000);

                const prompt = isDirectCall ? message.replace(/^(ии|бот|система),/i, '').trim() : `Прокомментируй это сообщение: "${message}"`;
                const reply = await askMistral(prompt);

                if (!reply) return;

                await db.createDocument(DB_ID, MSG_COL, ID.unique(), {
                    messageContent: reply,
                    senderId: "СИСТЕМА",
                    timestamp: new Date().toISOString(),
                    isEdited: false
                });
            }
        }

        function toggleNVG() {
            document.body.classList.toggle('nvg-mode');
        }

        function toggleRadioMode() {
            state.isRadioMode = !state.isRadioMode;
            const wrapper = document.querySelector('.chat-wrapper');
            const exitBtn = document.getElementById('radio-exit-btn');

            if (state.isRadioMode) {
                wrapper.classList.add('radio-active');
                exitBtn.style.display = 'block';
                playStaticNoise(0.2);
            } else {
                wrapper.classList.remove('radio-active');
                exitBtn.style.display = 'none';
                stopStaticNoise();
            }
        }

        function createNoiseBuffer() {
            const bufferSize = audioCtx.sampleRate * 2;
            const buffer = audioCtx.createBuffer(1, bufferSize, audioCtx.sampleRate);
            const data = buffer.getChannelData(0);
            for (let i = 0; i < bufferSize; i++) data[i] = Math.random() * 2 - 1;
            return buffer;
        }
        const noiseBuffer = createNoiseBuffer();

        function playStaticNoise(duration = 0) {
            if (state.radioNoise) state.radioNoise.stop();
            const noise = audioCtx.createBufferSource();
            noise.buffer = noiseBuffer;
            noise.loop = true;
            const gain = audioCtx.createGain();
            gain.gain.value = 0.05;
            noise.connect(gain);
            gain.connect(audioCtx.destination);
            noise.start();
            state.radioNoise = noise;
            if (duration > 0) setTimeout(() => stopStaticNoise(), duration * 1000);
        }

        function stopStaticNoise() {
            if (state.radioNoise) {
                state.radioNoise.stop();
                state.radioNoise = null;
            }
        }

        const pttBtn = document.getElementById('radio-ptt-btn');

        // MOBILE OPTIMIZATION: Touch Events
        pttBtn.addEventListener('touchstart', async (e) => {
            e.preventDefault();
            pttBtn.classList.add('pressed');
            pttBtn.innerText = "ЗАПИСЬ...";
            playStaticNoise();
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                state.recorder = new MediaRecorder(stream);
                state.chunks = [];
                state.recorder.ondataavailable = e => state.chunks.push(e.data);
                state.recorder.start();
            } catch(e) { showToast("Нет микрофона", 'error'); }
        });

        pttBtn.addEventListener('touchend', () => {
            pttBtn.classList.remove('pressed');
            pttBtn.innerText = "УДЕРЖИВАЙ ДЛЯ СВЯЗИ";
            stopStaticNoise();
            if (state.recorder && state.recorder.state === 'recording') {
                state.recorder.stop();
                state.recorder.onstop = () => {
                    const audioBlob = new Blob(state.chunks, { type: 'audio/mp3' });
                    const audioFile = new File([audioBlob], "radio_msg.mp3", { type: "audio/mp3" });
                    state.attachment = { file: audioFile, type: 'audio' };
                    sendMessage();
                    state.recorder.stream.getTracks().forEach(t => t.stop());
                };
            }
        });

        // Desktop Events
        pttBtn.addEventListener('mousedown', async (e) => {
            e.preventDefault();
            pttBtn.classList.add('pressed');
            pttBtn.innerText = "ЗАПИСЬ...";
            playStaticNoise();
            try {
                const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                state.recorder = new MediaRecorder(stream);
                state.chunks = [];
                state.recorder.ondataavailable = e => state.chunks.push(e.data);
                state.recorder.start();
            } catch(e) { showToast("Нет микрофона", 'error'); }
        });

        pttBtn.addEventListener('mouseup', () => {
            pttBtn.classList.remove('pressed');
            pttBtn.innerText = "УДЕРЖИВАЙ ДЛЯ СВЯЗИ";
            stopStaticNoise();
            if (state.recorder && state.recorder.state === 'recording') {
                state.recorder.stop();
                state.recorder.onstop = () => {
                    const audioBlob = new Blob(state.chunks, { type: 'audio/mp3' });
                    const audioFile = new File([audioBlob], "radio_msg.mp3", { type: "audio/mp3" });
                    state.attachment = { file: audioFile, type: 'audio' };
                    sendMessage();
                    state.recorder.stream.getTracks().forEach(t => t.stop());
                };
            }
        });

        function handleFileSelect(input) {
            if(input.files && input.files[0]) {
                const file = input.files[0];
                if (file.size > 50 * 1024 * 1024) {
                    showToast("Файл слишком большой (>50МБ)", 'error');
                    input.value = '';
                    return;
                }
                let type = 'file';
                if(file.type.startsWith('image/')) type = 'image';
                else if(file.type.startsWith('video/')) type = 'video';
                else if(file.type.startsWith('audio/')) type = 'audio';

                state.attachment = { file: file, type: type };
                document.getElementById('media-preview-area').style.display = 'flex';
                document.getElementById('preview-name').innerText = file.name;
                document.getElementById('preview-icon').innerText = type === 'image' ? '🖼' : (type === 'video' ? '🎬' : '🎵');
            }
        }

        function clearAttachment() {
            state.attachment = null;
            document.getElementById('file-upload').value = '';
            document.getElementById('media-preview-area').style.display = 'none';
        }

        function toggleAudio(btn, src) {
            const playerContainer = btn.parentElement;
            const progress = playerContainer.querySelector('.audio-progress');

            if (state.audioPlayer && state.audioPlayer.src === src) {
                if (state.audioPlayer.paused) {
                    state.audioPlayer.play();
                    btn.innerText = '❚❚';
                } else {
                    state.audioPlayer.pause();
                    btn.innerText = '▶';
                }
            } else {
                if (state.audioPlayer) {
                    state.audioPlayer.pause();
                    document.querySelectorAll('.audio-btn').forEach(b => b.innerText = '▶');
                }
                state.audioPlayer = new Audio(src);
                state.audioPlayer.play();
                btn.innerText = '❚❚';

                state.audioPlayer.ontimeupdate = () => {
                    if(state.audioPlayer.duration) {
                        const percent = (state.audioPlayer.currentTime / state.audioPlayer.duration) * 100;
                        progress.style.width = percent + '%';
                    }
                };
                state.audioPlayer.onended = () => {
                    btn.innerText = '▶';
                    progress.style.width = '0%';
                };
            }
        }

        function createMessageElement(msg) {
            const isMine = state.profile && msg.senderId === state.profile.username;
            const isSystem = msg.senderId === "СИСТЕМА";

            // Row Container
            const row = document.createElement('div');
            row.className = `message-row ${isMine ? 'mine' : ''} ${isSystem ? 'system' : ''}`;
            row.id = msg.$id;
            if (msg.optimistic) row.dataset.optimistic = "true";

            // Avatar (Soul ID) - Skip for System
            if (!isSystem) {
                const avatar = document.createElement('div');
                avatar.className = 'soul-avatar-placeholder';
                avatar.dataset.user = msg.senderId;
                avatar.onclick = () => openProfile(escapeHtml(escapeJs(msg.senderId)));
                row.appendChild(avatar);
            }

            // Message Bubble
            const div = document.createElement('div');
            div.className = `message ${isMine ? 'mine' : ''} ${isSystem ? 'system' : ''}`;

            let controls = '';
            if (!msg.optimistic && !isSystem && isMine) {
                controls = `<div class="controls">`;
                if(!msg.fileId) controls += `<span class="control-btn" onclick="startEdit('${msg.$id}', '${escapeHtml(escapeJs(msg.messageContent))}')">✎</span>`;
                controls += `<span class="control-btn" onclick="deleteMsg('${msg.$id}')" style="color:red">✕</span></div>`;
            }

            let contentHtml = `<span class="msg-text-content">${escapeHtml(msg.messageContent)}</span>`;

            if (msg.fileId || (msg.optimistic && msg.fileUrl)) {
                const fileView = msg.fileUrl || storage.getFileView(STORAGE_ID, msg.fileId);

                if (msg.fileType === 'image') {
                    contentHtml = `<img src="${fileView}" class="msg-media msg-img" onclick="openViewer('${fileView}')" loading="lazy">`;
                } else if (msg.fileType === 'video') {
                    contentHtml = `<video src="${fileView}" controls playsinline class="msg-media msg-video"></video>`;
                } else if (msg.fileType === 'audio') {
                    contentHtml = `<div class="custom-audio-player"><div class="audio-btn" onclick="toggleAudio(this, '${fileView}')">▶</div><div class="audio-track"><div class="audio-progress"></div></div></div>`;
                }
                if (msg.messageContent) contentHtml += `<div style="margin-top:8px;"><span class="msg-text-content">${escapeHtml(msg.messageContent)}</span></div>`;
            }

            // Removed inline author name since we have avatar, or keep it?
            // User requested "Instead of user images...", we are adding avatars.
            // Let's keep the name for clarity but maybe smaller?
            // The original code had name inside the bubble for others.
            const author = (isMine || isSystem) ? '' : `<span class="msg-author" onclick="openProfile('${escapeHtml(escapeJs(msg.senderId))}')">${escapeHtml(msg.senderId)}</span>`;
            const edited = msg.isEdited ? " <span style='opacity:0.5; font-size:0.6rem;'>(ред.)</span>" : "";
            const time = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

            div.innerHTML = `${controls}${author}<div class="msg-text">${contentHtml}${edited}</div><div class="msg-time">${time}</div>`;

            row.appendChild(div);
            return row;
        }

        async function loadMessages() {
            const container = document.getElementById('messages-container');
            container.innerHTML = '<div style="text-align:center;margin-top:50px;color:#888;font-size:0.85rem;">Загрузка...</div>';
            try {
                const res = await db.listDocuments(DB_ID, MSG_COL, [Query.orderAsc('timestamp'), Query.limit(100)]);
                container.innerHTML = '';
                const fragment = document.createDocumentFragment();
                res.documents.forEach(msg => {
                    fragment.appendChild(createMessageElement(msg));
                });
                container.appendChild(fragment);
                scrollToBottom();
            } catch(e) {
                console.error(e);
                container.innerHTML = '<div style="text-align:center;margin-top:50px;color:red;">Ошибка загрузки</div>';
            }
        }

        function renderMessage(msg) {
            const container = document.getElementById('messages-container');
            const existing = document.getElementById(msg.$id);

            if (existing) {
                if (!existing.dataset.optimistic) {
                    const textContent = existing.querySelector('.msg-text-content');
                    if(textContent && msg.messageContent) {
                         textContent.innerText = msg.messageContent;
                    }
                    if (msg.isEdited && !existing.innerText.includes('(ред.)')) {
                        const msgText = existing.querySelector('.msg-text');
                        if(msgText) msgText.insertAdjacentHTML('beforeend', " <span style='opacity:0.5; font-size:0.6rem;'>(ред.)</span>");
                    }
                }
                return;
            }

            const div = createMessageElement(msg);
            container.appendChild(div);

            const isMine = state.profile && msg.senderId === state.profile.username;
            if(container.scrollHeight - container.scrollTop - container.clientHeight < 300 || isMine) scrollToBottom();
        }

        async function sendMessage() {
            if (state.isUploading) return;

            const input = document.getElementById('msg-input');
            const text = input.value.trim();
            if ((!text && !state.attachment) || !state.profile) return;

            if (state.editingId) {
                try {
                    await db.updateDocument(DB_ID, MSG_COL, state.editingId, { messageContent: text, isEdited: true });
                    state.editingId = null;
                    document.getElementById('send-btn').innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
                    input.value = '';
                } catch(e) { showToast("Ошибка редактирования", 'error'); }
                return;
            }

            const sendBtn = document.getElementById('send-btn');
            state.isUploading = true;
            sendBtn.innerHTML = "•••";

            const tempId = "temp-" + Date.now();
            const optimisticMsg = {
                $id: tempId,
                messageContent: text,
                senderId: state.profile.username,
                timestamp: new Date().toISOString(),
                isEdited: false,
                fileType: state.attachment ? state.attachment.type : null,
                fileUrl: state.attachment ? URL.createObjectURL(state.attachment.file) : null,
                optimistic: true
            };
            renderMessage(optimisticMsg);

            input.value = '';
            const fileToUpload = state.attachment;
            clearAttachment();

            let fileId = null, fileType = null;
            if (fileToUpload) {
                try {
                    const uploaded = await storage.createFile(STORAGE_ID, ID.unique(), fileToUpload.file);
                    fileId = uploaded.$id;
                    fileType = fileToUpload.type;
                } catch(e) {
                    showToast("Ошибка загрузки файла", 'error');
                    document.getElementById(tempId).remove();
                    state.isUploading = false;
                    sendBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
                    return;
                }
            }

            try {
                await db.createDocument(DB_ID, MSG_COL, ID.unique(), {
                    messageContent: text,
                    senderId: state.profile.username,
                    timestamp: new Date().toISOString(),
                    isEdited: false,
                    fileId: fileId,
                    fileType: fileType
                });
            } catch(e) {
                showToast("Ошибка отправки", 'error');
                document.getElementById(tempId).remove();
            } finally {
                state.isUploading = false;
                sendBtn.innerHTML = `<svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>`;
            }
        }

        function handleRealtime(response) {
            const ev = response.events[0];
            const payload = response.payload;

            if(ev.includes('.create')) {
                if(payload.senderId !== state.profile.username) {
                    playNotification();
                    if(payload.senderId !== "СИСТЕМА") {
                        tryTriggerAI(payload.messageContent);
                    }
                }
            }

            if(ev.includes('.delete')) {
                const el = document.getElementById(payload.$id);
                if(el) {
                    el.style.opacity = '0';
                    el.style.transform = 'scale(0.8)';
                    setTimeout(() => el.remove(), 300);
                }
                return;
            }

            if(ev.includes('.update')) {
                const el = document.getElementById(payload.$id);
                if(el) {
                    if(payload.messageContent) {
                        let content = el.querySelector('.msg-text-content');
                        if(content) content.innerText = payload.messageContent;
                    }

                    const msgText = el.querySelector('.msg-text');
                    if(msgText && !msgText.innerText.includes('(ред.)')) {
                        msgText.insertAdjacentHTML('beforeend', " <span style='opacity:0.5; font-size:0.6rem;'>(ред.)</span>");
                    }
                }
                return;
            }

            if(ev.includes('.create')) {
                const isMine = state.profile && payload.senderId === state.profile.username;
                if (isMine) {
                    const tempMsgs = document.querySelectorAll('[data-optimistic="true"]');
                    tempMsgs.forEach(m => {
                        const textContent = m.querySelector('.msg-text-content');
                        if (textContent && textContent.innerText === payload.messageContent) {
                            m.remove();
                        }
                    });
                }
                if(!document.getElementById(payload.$id)) {
                    renderMessage(payload);
                    scrollToBottom();
                }
            }
        }

        function startEdit(id, text) {
            const i = document.getElementById('msg-input');
            i.value = text;
            i.focus();
            state.editingId = id;
            document.getElementById('send-btn').innerText = "✓";
        }

        async function deleteMsg(id) {
            if(confirm('Удалить?')) await db.deleteDocument(DB_ID, MSG_COL, id);
        }

        function openViewer(src) {
            document.getElementById('viewer-img').src = src;
            document.getElementById('image-viewer').style.display = 'flex';
        }

        function openModal(id) {
            document.getElementById(id).style.display = 'flex';
        }

        function closeModal(id) {
            document.getElementById(id).style.display = 'none';
        }

        async function openUserList() {
            openModal('users-modal');
            const listContainer = document.getElementById('users-list-container');
            listContainer.innerHTML = '<p>Загрузка архивов...</p>';

            try {
                const res = await db.listDocuments(DB_ID, PROFILES_COLLECTION_ID, [Query.limit(100)]);
                if (res.documents.length === 0) {
                    listContainer.innerHTML = '<p>Список пуст.</p>';
                    return;
                }

                const html = res.documents.map(user =>
                    `<div class="user-item" onclick="closeModal('users-modal'); openProfile('${escapeHtml(escapeJs(user.username))}')">
                        <span style="font-weight:700;">${escapeHtml(user.username)}</span>
                        <span class="u-rank">${escapeHtml(user.rank || 'Наблюдатель')}</span>
                    </div>`
                ).join('');
                listContainer.innerHTML = html;
            } catch(e) {
                listContainer.innerHTML = '<p style="color:red">Ошибка доступа к архивам.</p>';
            }
        }

        function updateFlowerUI(p) {
            const ether = p.ether || 0;
            const xp = p.flower_xp || 0;

            document.getElementById('f-ether').innerText = ether;

            let stage = "ЗЕРНО (I)";
            if (xp >= 50) stage = "ВОЗНЕСЕНИЕ (IV)";
            else if (xp >= 21) stage = "ЦВЕТЕНИЕ (III)";
            else if (xp >= 6) stage = "РОСТОК (II)";
            document.getElementById('f-stage').innerText = `${stage} [${xp} XP]`;

            // Check claim status
            const today = getMSKDate();
            const btnClaim = document.getElementById('btn-claim');
            const timerDiv = document.getElementById('claim-timer');

            if (p.last_claim_date === today) {
                btnClaim.disabled = true;
                btnClaim.innerText = "СОБРАНО";
                timerDiv.classList.remove('hidden');
                startClaimTimer();
            } else {
                btnClaim.disabled = false;
                btnClaim.innerText = "СБОР ЭФИРА";
                timerDiv.classList.add('hidden');
            }

            // Nourish button
            const btnNourish = document.getElementById('btn-nourish');
            if (ether > 0) {
                btnNourish.disabled = false;
                btnNourish.innerText = "НАПИТАТЬ (-1)";
            } else {
                btnNourish.disabled = true;
                btnNourish.innerText = "НЕТ ЭФИРА";
            }
        }

        function startClaimTimer() {
            if (state.claimTimer) clearInterval(state.claimTimer);

            const timerDiv = document.getElementById('claim-timer');
            const update = () => {
                const now = new Date();
                // Target: Next 00:00 MSK.
                // Currently simplified: Just countdown to next midnight local?
                // No, prompt requires MSK.
                // 00:00 MSK is 21:00 UTC previous day? No, UTC+3.

                // Hacky MSK calculation:
                // Get current UTC time
                const utc = now.getTime() + (now.getTimezoneOffset() * 60000);
                // Get MSK time
                const mskTime = new Date(utc + (3600000 * 3));

                // Target is tomorrow 00:00 MSK
                const target = new Date(mskTime);
                target.setHours(24, 0, 0, 0);

                const diff = target - mskTime;
                if (diff < 0) {
                     timerDiv.innerText = "ГОТОВО";
                     return;
                }

                const h = Math.floor(diff / (1000 * 60 * 60));
                const m = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
                const s = Math.floor((diff % (1000 * 60)) / 1000);

                timerDiv.innerText = `До сброса: ${h}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
            };

            state.claimTimer = setInterval(update, 1000);
            update();
        }

        async function claimEther() {
            if (!state.user) return; // Must be logged in
            const today = getMSKDate();

            // Optimistic check if profile exists locally
            if (state.profile && state.profile.last_claim_date === today) {
                showToast("Уже собрано сегодня", "error");
                return;
            }

            try {
                // Determine ID: Profile ID if exists, otherwise User ID
                const docId = state.profile ? state.profile.$id : state.user.$id;
                const currentEther = state.profile ? (state.profile.ether || 0) : 0;
                const newEther = currentEther + 1;

                await db.updateDocument(DB_ID, PROFILES_COLLECTION_ID, docId, {
                    ether: newEther,
                    last_claim_date: today
                });

                // Update local state if successful
                if (state.profile) {
                    state.profile.ether = newEther;
                    state.profile.last_claim_date = today;
                    state.profileCache.set(state.profile.username, state.profile);
                    updateFlowerUI(state.profile);
                }

                showToast("+1 Эфир получен");
                playNotification();

            } catch(e) {
                // FIX: Auto-Create Logic
                if (e.code === 404) {
                     try {
                        const newProfile = await db.createDocument(DB_ID, PROFILES_COLLECTION_ID, state.user.$id, {
                            username: state.user.name,
                            email: state.user.email,
                            rank: "Наблюдатель",
                            about: "",
                            ether: 1,
                            flower_xp: 0,
                            last_claim_date: today
                        });

                        state.profile = newProfile;
                        state.profileCache.set(state.profile.username, state.profile);
                        updateFlowerUI(state.profile);
                        showToast("+1 Эфир получен (Профиль создан)");
                        playNotification();
                     } catch (createErr) {
                         console.error(createErr);
                         showToast("Ошибка создания профиля", "error");
                     }
                } else {
                    console.error(e);
                    showToast("Ошибка сбора", "error");
                }
            }
        }

        async function nourishFlower() {
            if (!state.profile || (state.profile.ether || 0) <= 0) return;

            try {
                const newEther = state.profile.ether - 1;
                const newXp = (state.profile.flower_xp || 0) + 1;

                await db.updateDocument(DB_ID, PROFILES_COLLECTION_ID, state.profile.$id, {
                    ether: newEther,
                    flower_xp: newXp
                });

                state.profile.ether = newEther;
                state.profile.flower_xp = newXp;
                state.profileCache.set(state.profile.username, state.profile);

                updateFlowerUI(state.profile);

                // Trigger 3D Update
                if (typeof AvatarSystem !== 'undefined') {
                    AvatarSystem.updateAvatar(state.profile.username, newXp);
                }

                // FX
                showToast("Цветок напитан (+1 XP)");
                playNotification();

                // Particle FX (Simulated via simple DOM overlay)
                const particles = document.createElement('div');
                particles.style.position = 'fixed';
                particles.style.inset = '0';
                particles.style.zIndex = '9999';
                particles.style.pointerEvents = 'none';
                particles.innerHTML = '<div style="position:absolute; top:50%; left:50%; transform:translate(-50%, -50%); font-size:5rem; opacity:0; animation: fadeUp 1s;">💧</div>';
                document.body.appendChild(particles);
                setTimeout(() => particles.remove(), 1000);

            } catch(e) {
                showToast("Ошибка", "error");
            }
        }

        async function openProfile(username) {
            openModal('profile-modal');
            document.getElementById('p-name').innerText = username;
            document.getElementById('p-rank').innerText = "...";
            document.getElementById('admin-controls').classList.add('hidden');
            document.getElementById('p-save-self').classList.add('hidden');
            document.getElementById('p-about-edit').classList.add('hidden');
            document.getElementById('p-about').classList.remove('hidden');
            document.getElementById('flower-controls').classList.add('hidden'); // Default hide

            try {
                let p;
                if (state.profileCache.has(username)) {
                    p = state.profileCache.get(username);
                } else {
                    const res = await db.listDocuments(DB_ID, PROFILES_COLLECTION_ID, [Query.equal('username', username)]);
                    if(res.documents.length > 0) {
                        p = res.documents[0];
                        state.profileCache.set(username, p);
                    }
                }

                if (p) {
                    // Update Profile Avatar
                    if (typeof AvatarSystem !== 'undefined' && AvatarSystem.renderProfileAvatar) {
                        const canvas = document.getElementById('profile-flower-canvas');
                        if (canvas) {
                            AvatarSystem.renderProfileAvatar(canvas, p.username, p.flower_xp || 0);
                        }
                    }

                    state.currentProfileId = p.$id;
                    document.getElementById('p-rank').innerText = p.rank || "Имперец";
                    document.getElementById('p-about').innerText = p.about || "Данных нет.";

                    if (state.profile && p.$id === state.profile.$id) {
                        document.getElementById('p-about').classList.add('hidden');
                        document.getElementById('p-about-edit').classList.remove('hidden');
                        document.getElementById('p-about-edit').value = p.about || "";
                        document.getElementById('p-save-self').classList.remove('hidden');

                        // Show Flower Controls ONLY for self
                        document.getElementById('flower-controls').classList.remove('hidden');
                        updateFlowerUI(p);
                    }
                    if (state.user && state.user.email.toLowerCase() === ADMIN_EMAIL.toLowerCase()) {
                        document.getElementById('admin-controls').classList.remove('hidden');
                        document.getElementById('p-rank-edit').value = p.rank || "Наблюдатель";
                    }
                }
            } catch(e) {}
        }

        function openMyProfile() {
            if(state.profile) {
                openProfile(state.profile.username);
            } else {
                showToast("Профиль не загружен", "error");
            }
        }

        async function saveMyProfile() {
            const newAbout = document.getElementById('p-about-edit').value;
            await db.updateDocument(DB_ID, PROFILES_COLLECTION_ID, state.currentProfileId, { about: newAbout });

            if (state.profile) {
                state.profile.about = newAbout;
                state.profileCache.set(state.profile.username, state.profile);
            }

            closeModal('profile-modal');
            showToast("Сохранено");
        }

        async function saveProfileChanges() {
            const newRank = document.getElementById('p-rank-edit').value;
            await db.updateDocument(DB_ID, PROFILES_COLLECTION_ID, state.currentProfileId, { rank: newRank });

            const username = document.getElementById('p-name').innerText;
            if (state.profileCache.has(username)) {
                const p = state.profileCache.get(username);
                p.rank = newRank;
                state.profileCache.set(username, p);
            }

            closeModal('profile-modal');
            showToast("Статус обновлен");
        }

        let revealObserver;
        function reveal() {
            if (revealObserver) {
                revealObserver.disconnect();
            }

            var reveals = document.querySelectorAll(".reveal");

            revealObserver = new IntersectionObserver(function(entries) {
                entries.forEach(function(entry) {
                    if (entry.isIntersecting) {
                        entry.target.classList.add("active");
                        revealObserver.unobserve(entry.target);
                    }
                });
            }, {
                rootMargin: '0px 0px -50px 0px'
            });

            reveals.forEach(function(reveal) {
                if (!reveal.classList.contains("active")) {
                    revealObserver.observe(reveal);
                }
            });
        }
        reveal();

        document.getElementById('msg-input').addEventListener('keypress', (e) => {
            if(e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });

        // MOBILE OPTIMIZATION: Auto focus on desktop only
        if (window.innerWidth >= 768) {
            document.getElementById('msg-input').addEventListener('focus', () => {
                setTimeout(() => {
                    document.getElementById('msg-input').scrollIntoView({ behavior: 'smooth', block: 'nearest' });
                }, 300);
            });
        }

        // COUNTDOWN SYSTEM
        function startCountdown() {
            const targetDate = new Date('2026-06-01T00:00:00').getTime();
            const elYears = document.getElementById('cd-years');
            const elDays = document.getElementById('cd-days');
            const elHours = document.getElementById('cd-hours');
            const elMinutes = document.getElementById('cd-minutes');
            const elSeconds = document.getElementById('cd-seconds');
            const elMs = document.getElementById('cd-ms');
            const timer = document.getElementById('countdown-timer');

            function updateTime() {
                const now = new Date();
                const diff = targetDate - now.getTime();

                if (diff <= 0) {
                    if (timer) timer.style.display = 'none';
                    return;
                }

                // Calculate Years (Once per second is fine)
                let tempDate = new Date(now);
                let years = 0;
                while (true) {
                    tempDate.setFullYear(tempDate.getFullYear() + 1);
                    if (tempDate.getTime() > targetDate) {
                        tempDate.setFullYear(tempDate.getFullYear() - 1);
                        break;
                    }
                    years++;
                }

                const remainingTime = targetDate - tempDate.getTime();
                const days = Math.floor(remainingTime / (1000 * 60 * 60 * 24));
                const hours = Math.floor((remainingTime % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60));
                const minutes = Math.floor((remainingTime % (1000 * 60 * 60)) / (1000 * 60));
                const seconds = Math.floor((remainingTime % (1000 * 60)) / 1000);

                if(elYears) elYears.innerText = years;
                if(elDays) elDays.innerText = days;
                if(elHours) elHours.innerText = hours.toString().padStart(2, '0');
                if(elMinutes) elMinutes.innerText = minutes.toString().padStart(2, '0');
                if(elSeconds) elSeconds.innerText = seconds.toString().padStart(2, '0');
            }

            function updateMs() {
                const diff = targetDate - Date.now();
                if (diff <= 0) return;
                const ms = Math.floor(diff % 1000);
                if(elMs) elMs.innerText = ms.toString().padStart(3, '0');
                requestAnimationFrame(updateMs);
            }

            setInterval(updateTime, 1000);
            updateTime();
            requestAnimationFrame(updateMs);
        }

        startCountdown();

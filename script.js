        // CONFIGURATION
        const PROJECT_ID = '69624669002d880cd7bb';
        const ENDPOINT = 'https://fra.cloud.appwrite.io/v1';
        const DB_ID = '6962475a003af27425fb';
        const MSG_COL = 'verachkichathistory';
        const PROFILES_COL = 'profiles';
        const STORAGE_ID = '696363f30004cb97e6a1';
        const ADMIN_EMAIL = "kraacovstepa@gmail.com";
        const SECRET_CODE = "GLEB2023";

        const keyP1 = "hf_UwcAeGYbQKgyWa";
        const keyP2 = "AlccfNJwQoCAxVzHgSdS";
        const HF_TOKEN = keyP1 + keyP2;

        // ENIGMA ENCRYPTION SYSTEM
        const encryptedMessages = {};

        function getRandomChar() {
            const chars = '#@!$%^&*()_+-=[]{}|;:,.<>?/~';
            return chars[Math.floor(Math.random() * chars.length)];
        }

        function scrambleText(text) {
            return text.split('').map(c => c.trim() === '' ? c : getRandomChar()).join('');
        }

        function decryptMessage(textId, btnId) {
            const el = document.getElementById(textId);
            const btn = document.getElementById(btnId);
            if (!el || !encryptedMessages[textId]) return;

            if (btn) btn.style.display = 'none';

            const originalText = encryptedMessages[textId];
            let revealIndex = 0;

            const interval = setInterval(() => {
                const currentText = originalText.split('').map((char, index) => {
                    if (index < revealIndex) return char;
                    return char.trim() === '' ? char : getRandomChar();
                }).join('');

                el.innerText = currentText;
                revealIndex += 0.5;

                if (revealIndex >= originalText.length) {
                    clearInterval(interval);
                    el.innerText = originalText;
                    el.classList.remove('encrypted');
                    delete encryptedMessages[textId];
                }
            }, 30);
        }

        // APPWRITE SETUP
        const { Client, Account, Databases, Storage, ID, Query } = Appwrite;
        const client = new Client().setEndpoint(ENDPOINT).setProject(PROJECT_ID);
        const account = new Account(client);
        const db = new Databases(client);
        const storage = new Storage(client);

        // GLOBAL STATE
        let state = {
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
            geigerVal: 0,
            aiCooldown: false
        };

        const audioCtx = new (window.AudioContext || window.webkitAudioContext)();

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
            let vh = window.innerHeight * 0.01;
            document.documentElement.style.setProperty('--vh', `${vh}px`);
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
            return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
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
                    const res = await db.listDocuments(DB_ID, PROFILES_COL, [Query.equal('email', state.user.email)]);
                if(res.documents.length > 0) {
                    state.profile = res.documents[0];
                    state.profileCache.set(state.profile.username, state.profile);
                }
                    else state.profile = await db.createDocument(DB_ID, PROFILES_COL, ID.unique(), { username: state.user.name, email: state.user.email, rank: "Наблюдатель", about: "" });
                } catch(e) { console.log("Profile create/fetch error", e); }

                if(state.profile && state.profile.rank === 'Изгнан') { document.getElementById('ban-screen').style.display = 'flex'; return; }
                showApp();
            } catch (e) { showLanding(); }
        }
        checkSession();

        function showApp() {
            document.querySelectorAll('section:not(#app-interface)').forEach(el => el.classList.add('hidden'));
            document.querySelector('footer').style.display = 'none';
            document.getElementById('app-interface').classList.remove('hidden');
            document.getElementById('nav-guest').classList.add('hidden');
            document.getElementById('nav-user').classList.remove('hidden');
            closeModal('auth-modal');
            if(state.profile) {
                document.getElementById('nav-username').innerText = state.profile.username;
                document.getElementById('nav-rank').innerText = state.profile.rank || "Имперец";
            }
            loadMessages();
            client.subscribe(`databases.${DB_ID}.collections.${MSG_COL}.documents`, handleRealtime);
            startGeigerLoop();
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
            document.getElementById('nav-guest').classList.remove('hidden');
            document.getElementById('nav-user').classList.add('hidden');
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
                    await db.createDocument(DB_ID, PROFILES_COL, ID.unique(), { username: name, email: email, rank: "Наблюдатель", about: "" });
                    location.reload();
                }
            } catch(e) { showToast(e.message, 'error'); }
        }

        async function logout() {
            await account.deleteSession('current');
            location.reload();
        }

        async function askMistral(prompt, isReport = false) {
            try {
                const systemPrompt = isReport
                    ? "Ты — СИСТЕМА, аналитический модуль чата 'Верачки'. Сделай КРАТКИЙ, но информативный отчет по этой переписке. Кто что писал, основные темы, конфликты. Будь холоден и точен."
                    : "Ты — СИСТЕМА, искусственный интеллект-наблюдатель чата 'Верачки'. Твой характер: ироничный, загадочный, киберпанковый. Ты не человек. Отвечай кратко (1-2 предложения).";

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
                            parameters: { max_new_tokens: isReport ? 300 : 100, return_full_text: false }
                        }),
                    }
                );

                if (!response.ok) throw new Error("AI Error");
                const result = await response.json();
                return result[0].generated_text.trim();
            } catch (error) {
                console.error(error);
                return "Ошибка связи с ядром.";
            }
        }

        async function generateReport() {
            openModal('report-modal');
            const content = document.getElementById('report-content');
            content.innerText = "Сканирование архивов...";

            const msgs = Array.from(document.querySelectorAll('.message:not(.system) .msg-text-content'))
                .slice(-30)
                .map(el => {
                    const author = el.closest('.message').querySelector('.msg-author')?.innerText || "Я";
                    return `${author}: ${el.innerText}`;
                })
                .join("\n");

            if (msgs.length < 50) {
                content.innerText = "Недостаточно данных для анализа.";
                return;
            }

            const report = await askMistral(msgs, true);
            content.innerText = report;
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

                await db.createDocument(DB_ID, MSG_COL, ID.unique(), {
                    messageContent: reply,
                    senderId: "СИСТЕМА",
                    timestamp: new Date().toISOString(),
                    isEdited: false
                });
            }
        }

        function setDefcon(level) {
            document.body.classList.remove('defcon-1');
            document.querySelectorAll('.defcon-lvl').forEach(el => el.classList.remove('active'));
            const activeBtn = document.getElementById(`def-${level}`);
            if(activeBtn) activeBtn.classList.add('active');

            if (level === 1) {
                document.body.classList.add('defcon-1');
                playGeigerClick(0.1);
            }
        }

        function toggleNVG() {
            document.body.classList.toggle('nvg-mode');
            playGeigerClick();
        }

        function playGeigerClick(vol = 0.05) {
            const osc = audioCtx.createOscillator();
            const gain = audioCtx.createGain();
            osc.connect(gain);
            gain.connect(audioCtx.destination);
            osc.type = 'square';
            osc.frequency.value = 100 + Math.random() * 50;
            gain.gain.value = vol;
            osc.start();
            setTimeout(() => osc.stop(), 0.01);
        }

        function startGeigerLoop() {
            let lastTime = 0;
            const needle = document.getElementById('geiger-needle');
            const loop = (time) => {
                if (!lastTime) lastTime = time;
                const dt = Math.min(time - lastTime, 100); // Cap dt to avoid huge jumps
                lastTime = time;

                if (state.geigerVal > 0) {
                    state.geigerVal *= Math.pow(0.95, dt / 100);
                    if (state.geigerVal < 0.001) state.geigerVal = 0;

                    if (needle) {
                        const rotation = -45 + (state.geigerVal * 90);
                        needle.style.transform = `rotate(${Math.min(45, rotation)}deg)`;
                    }

                    if (Math.random() < state.geigerVal * 0.5 * (dt / 100)) playGeigerClick();
                }
                requestAnimationFrame(loop);
            };
            requestAnimationFrame(loop);
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

            const div = document.createElement('div');
            div.className = `message ${isMine ? 'mine' : ''} ${isSystem ? 'system' : ''}`;
            div.id = msg.$id;
            if (msg.optimistic) div.dataset.optimistic = "true";

            let controls = '';
            if (!msg.optimistic && !isSystem && isMine) {
                controls = `<div class="controls">`;
                if(!msg.fileId) controls += `<span class="control-btn" onclick="startEdit('${msg.$id}', \`${escapeHtml(msg.messageContent)}\`)">✎</span>`;
                controls += `<span class="control-btn" onclick="deleteMsg('${msg.$id}')" style="color:red">✕</span></div>`;
            }

            const uniqueId = msg.$id || `temp-${Math.random().toString(36).substr(2, 9)}`;
            const textId = `enc-${uniqueId}`;
            const btnId = `btn-${uniqueId}`;

            let encryptedHtml = '';
            if (msg.messageContent) {
                encryptedMessages[textId] = msg.messageContent;
                const scrambled = scrambleText(msg.messageContent);
                encryptedHtml = `<span id="${textId}" class="msg-text-content encrypted">${scrambled}</span><span id="${btnId}" class="decipher-icon" onclick="decryptMessage('${textId}', '${btnId}')" title="Расшифровать">🔒</span>`;
            } else {
                encryptedHtml = `<span class="msg-text-content"></span>`;
            }

            let contentHtml = encryptedHtml;

            if (msg.fileId || (msg.optimistic && msg.fileUrl)) {
                const fileView = msg.fileUrl || storage.getFileView(STORAGE_ID, msg.fileId);

                if (msg.fileType === 'image') {
                    contentHtml = `<img src="${fileView}" class="msg-media msg-img" onclick="openViewer('${fileView}')" loading="lazy">`;
                } else if (msg.fileType === 'video') {
                    contentHtml = `<video src="${fileView}" controls playsinline class="msg-media msg-video"></video>`;
                } else if (msg.fileType === 'audio') {
                    contentHtml = `<div class="custom-audio-player"><div class="audio-btn" onclick="toggleAudio(this, '${fileView}')">▶</div><div class="audio-track"><div class="audio-progress"></div></div></div>`;
                }
                if (msg.messageContent) contentHtml += `<div style="margin-top:8px;">${encryptedHtml}</div>`;
            }

            const author = (isMine || isSystem) ? '' : `<span class="msg-author" onclick="openProfile('${msg.senderId}')">${msg.senderId}</span>`;
            const edited = msg.isEdited ? " <span style='opacity:0.5; font-size:0.6rem;'>(ред.)</span>" : "";
            const time = new Date(msg.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});

            div.innerHTML = `${controls}${author}<div class="msg-text">${contentHtml}${edited}</div><div class="msg-time">${time}</div>`;
            return div;
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
                    if(textContent) {
                         const uniqueId = msg.$id;
                         const textId = `enc-${uniqueId}`;
                         encryptedMessages[textId] = msg.messageContent || "";
                         textContent.innerText = scrambleText(msg.messageContent || "");
                         textContent.classList.add('encrypted');
                         const btn = existing.querySelector('.decipher-icon');
                         if(btn) btn.style.display = 'inline-block';
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
                state.geigerVal = Math.min(1, state.geigerVal + 0.3);

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
                    const textId = `enc-${payload.$id}`;
                    const btnId = `btn-${payload.$id}`;

                    if(payload.messageContent) {
                        encryptedMessages[textId] = payload.messageContent;

                        let content = document.getElementById(textId);
                        if(!content) content = el.querySelector('.msg-text-content');

                        if(content) {
                            content.innerText = scrambleText(payload.messageContent);
                            content.classList.add('encrypted');
                            content.id = textId;

                            let btn = document.getElementById(btnId);
                            if(!btn) btn = el.querySelector('.decipher-icon');

                            if(btn) {
                                btn.style.display = 'inline-block';
                            } else {
                                content.insertAdjacentHTML('afterend', `<span id="${btnId}" class="decipher-icon" onclick="decryptMessage('${textId}', '${btnId}')" title="Расшифровать">🔒</span>`);
                            }
                        }
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
                        const textId = `enc-${m.id}`;
                        const storedContent = encryptedMessages[textId];
                        const textContent = m.querySelector('.msg-text-content');

                        if ((storedContent && storedContent === payload.messageContent) ||
                            (textContent && textContent.innerText === payload.messageContent)) {
                            delete encryptedMessages[textId];
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
                const res = await db.listDocuments(DB_ID, PROFILES_COL, [Query.limit(100)]);
                if (res.documents.length === 0) {
                    listContainer.innerHTML = '<p>Список пуст.</p>';
                    return;
                }

                const html = res.documents.map(user =>
                    `<div class="user-item" onclick="closeModal('users-modal'); openProfile('${user.username}')">
                        <span style="font-weight:700;">${user.username}</span>
                        <span class="u-rank">${user.rank || 'Наблюдатель'}</span>
                    </div>`
                ).join('');
                listContainer.innerHTML = html;
            } catch(e) {
                listContainer.innerHTML = '<p style="color:red">Ошибка доступа к архивам.</p>';
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

            try {
                let p;
                if (state.profileCache.has(username)) {
                    p = state.profileCache.get(username);
                } else {
                    const res = await db.listDocuments(DB_ID, PROFILES_COL, [Query.equal('username', username)]);
                    if(res.documents.length > 0) {
                        p = res.documents[0];
                        state.profileCache.set(username, p);
                    }
                }

                if (p) {
                    state.currentProfileId = p.$id;
                    document.getElementById('p-rank').innerText = p.rank || "Имперец";
                    document.getElementById('p-about').innerText = p.about || "Данных нет.";

                    if (state.profile && p.$id === state.profile.$id) {
                        document.getElementById('p-about').classList.add('hidden');
                        document.getElementById('p-about-edit').classList.remove('hidden');
                        document.getElementById('p-about-edit').value = p.about || "";
                        document.getElementById('p-save-self').classList.remove('hidden');
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
            await db.updateDocument(DB_ID, PROFILES_COL, state.currentProfileId, { about: newAbout });

            if (state.profile) {
                state.profile.about = newAbout;
                state.profileCache.set(state.profile.username, state.profile);
            }

            closeModal('profile-modal');
            showToast("Сохранено");
        }

        async function saveProfileChanges() {
            const newRank = document.getElementById('p-rank-edit').value;
            await db.updateDocument(DB_ID, PROFILES_COL, state.currentProfileId, { rank: newRank });

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

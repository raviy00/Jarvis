# modules/web_gui.py - Jarvis Dashboard with Real-time SSE bridge
from flask import Flask, request, jsonify, send_file, Response
from modules.brain import think
from modules.memory import load_memory, add_message
from modules.transcriber import transcribe_audio
from modules.speaker import text_to_audio_file
import os
import tempfile
import queue
import json
import time

app = Flask(__name__)

# Global SSE queue — voice_listener pushes events here, browser reads them
_event_queue: queue.Queue = queue.Queue(maxsize=50)

def push_event(role: str, text: str):
    """Push a conversation event to all connected browser clients."""
    try:
        _event_queue.put_nowait({"role": role, "text": text})
    except queue.Full:
        pass  # Drop if nobody is listening

DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>JARVIS | Holographic HUD</title>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Rajdhani:wght@300;500;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --glow-color: #ffaa00;
            --accent-color: #ffcc00;
            --bg-dark: #050300;
            --panel-bg: rgba(255, 170, 0, 0.03);
            --border-glow: rgba(255, 170, 0, 0.4);
            --hologram-flicker: rgba(255, 170, 0, 0.1);
        }

        @keyframes flicker {
            0% { opacity: 0.9; }
            5% { opacity: 0.8; }
            10% { opacity: 0.9; }
            15% { opacity: 0.7; }
            20% { opacity: 0.9; }
            25% { opacity: 1; }
            80% { opacity: 0.9; }
            100% { opacity: 1; }
        }

        * { box-sizing: border-box; margin: 0; padding: 0; }
        
        body {
            background-color: var(--bg-dark);
            color: var(--glow-color);
            font-family: 'Rajdhani', sans-serif;
            height: 100vh;
            overflow: hidden;
            display: flex;
            align-items: center;
            justify-content: center;
            background: radial-gradient(circle at center, #1a1000 0%, #050300 100%);
            animation: flicker 4s infinite;
        }

        /* --- Holographic Background --- */
        .grid {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background-image: 
                linear-gradient(rgba(255, 170, 0, 0.05) 1px, transparent 1px),
                linear-gradient(90deg, rgba(255, 170, 0, 0.05) 1px, transparent 1px);
            background-size: 40px 40px;
            z-index: -1;
            mask-image: radial-gradient(circle, black 30%, transparent 80%);
        }

        .scanline {
            position: fixed;
            top: 0; left: 0; width: 100%; height: 100%;
            background: linear-gradient(to bottom, transparent 40%, rgba(255, 170, 0, 0.05) 50%, transparent 60%);
            background-size: 100% 10px;
            pointer-events: none;
            z-index: 10;
            animation: scan 8s linear infinite;
        }
        @keyframes scan { from { transform: translateY(-100%); } to { transform: translateY(100%); } }

        /* --- HUD Layout --- */
        .hud-container {
            position: relative;
            width: 100vw;
            height: 100vh;
            display: grid;
            grid-template-columns: 350px 1fr 350px;
            grid-template-rows: 80px 1fr 180px;
            padding: 30px;
            gap: 30px;
        }

        /* --- Complex Holographic Center --- */
        .center-hud {
            grid-column: 2;
            grid-row: 2;
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
        }

        .ring-container {
            position: relative;
            width: 600px;
            height: 600px;
            display: flex;
            align-items: center;
            justify-content: center;
            filter: drop-shadow(0 0 15px var(--glow-color));
        }

        .ring {
            position: absolute;
            border-radius: 50%;
            border: 1px solid var(--border-glow);
            transition: 0.5s;
        }

        /* Intricate Movie-Style Rings */
        .ring-outer { width: 550px; height: 550px; border-style: double; border-width: 3px; border-left-color: transparent; border-right-color: transparent; animation: rotate 30s linear infinite; }
        .ring-mid { width: 480px; height: 480px; border-style: dashed; border-width: 1px; animation: rotate 20s linear infinite reverse; }
        .ring-inner { width: 400px; height: 400px; border-top-color: transparent; border-bottom-color: transparent; border-width: 2px; border-style: solid; animation: rotate 12s linear infinite; }
        .ring-core { width: 320px; height: 320px; border: 1px dashed var(--glow-color); opacity: 0.3; animation: rotate 40s linear infinite; }
        
        /* Arc Reactor Core */
        .core {
            width: 150px;
            height: 150px;
            background: radial-gradient(circle, var(--accent-color) 0%, rgba(255, 170, 0, 0.2) 50%, transparent 100%);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            cursor: pointer;
            z-index: 5;
            transition: 0.4s;
            box-shadow: 0 0 50px var(--glow-color), inset 0 0 20px #fff;
            border: 2px solid #fff;
        }

        .core::after {
            content: '';
            position: absolute;
            width: 180px; height: 180px;
            border: 2px solid var(--glow-color);
            border-radius: 50%;
            animation: pulse-ring 2s infinite;
        }

        @keyframes pulse-ring { 0% { transform: scale(0.8); opacity: 1; } 100% { transform: scale(1.4); opacity: 0; } }

        .core:hover { transform: scale(1.05); box-shadow: 0 0 80px var(--glow-color); }
        .core.recording { background: radial-gradient(circle, #ff0000 0%, #330000 100%); box-shadow: 0 0 60px #ff0000; border-color: #ffaaaa; }
        
        .core svg { width: 60px; height: 60px; fill: #fff; filter: drop-shadow(0 0 10px #fff); }

        /* --- Panels --- */
        .panel {
            background: var(--panel-bg);
            border: 1px solid var(--border-glow);
            backdrop-filter: blur(5px);
            padding: 20px;
            display: flex;
            flex-direction: column;
            clip-path: polygon(15% 0, 85% 0, 100% 15%, 100% 85%, 85% 100%, 15% 100%, 0 85%, 0 15%);
            animation: panel-in 1s cubic-bezier(0.17, 0.67, 0.83, 0.67);
        }

        @keyframes panel-in { from { opacity: 0; transform: scale(0.9); } to { opacity: 1; transform: scale(1); } }

        .top-info { grid-column: 1 / span 3; display: flex; justify-content: space-between; align-items: flex-end; padding: 0 50px; border-bottom: 2px solid var(--border-glow); margin-bottom: 10px; }
        .logo { font-family: 'Orbitron', sans-serif; font-size: 2.2rem; font-weight: 700; letter-spacing: 8px; color: #fff; text-shadow: 0 0 20px var(--glow-color); }
        .status-txt { font-size: 1rem; text-transform: uppercase; letter-spacing: 3px; font-weight: 700; color: var(--glow-color); }

        /* --- Side Metrics --- */
        .side-metric { margin-bottom: 25px; }
        .m-label { font-size: 0.7rem; font-weight: 700; opacity: 0.8; margin-bottom: 5px; display: block; }
        .m-bar { height: 6px; background: rgba(255, 170, 0, 0.1); border: 1px solid var(--border-glow); position: relative; }
        .m-fill { height: 100%; background: linear-gradient(90deg, var(--glow-color), #fff); box-shadow: 0 0 10px var(--glow-color); transition: 1s; }

        .code-stream { font-family: monospace; font-size: 0.65rem; color: var(--glow-color); opacity: 0.5; overflow: hidden; height: 150px; }

        /* --- Interactive Chat Panel --- */
        .chat-panel {
            grid-column: 2;
            grid-row: 3;
            height: 160px;
            display: flex;
            flex-direction: column;
            gap: 12px;
            background: rgba(255, 170, 0, 0.05);
            border-bottom: none;
            clip-path: polygon(5% 0, 95% 0, 100% 20%, 100% 100%, 0 100%, 0 20%);
        }

        .chat-box {
            flex: 1;
            overflow-y: auto;
            padding: 10px 20px;
            font-size: 1.1rem;
            display: flex;
            flex-direction: column;
            gap: 10px;
            scrollbar-width: thin;
        }
        .chat-box::-webkit-scrollbar { display: none; }

        .msg { padding: 10px 15px; border-right: 3px solid var(--glow-color); background: rgba(255, 170, 0, 0.08); margin-bottom: 5px; position: relative; }
        .msg.user { border-right: none; border-left: 3px solid #fff; color: #fff; align-self: flex-start; }
        .msg.jarvis { border-right-color: var(--glow-color); align-self: flex-end; text-align: right; }

        .input-group { display: flex; gap: 15px; padding: 0 20px 10px 20px; }
        .input-group input {
            flex: 1;
            background: rgba(0,0,0,0.5);
            border: 1px solid var(--border-glow);
            padding: 12px 20px;
            color: #fff;
            font-family: 'Rajdhani', sans-serif;
            font-size: 1.1rem;
            outline: none;
            box-shadow: inset 0 0 10px rgba(255, 170, 0, 0.2);
        }
        .input-group button {
            background: var(--glow-color);
            border: none;
            padding: 0 30px;
            color: #000;
            font-weight: 800;
            cursor: pointer;
            font-family: 'Rajdhani', sans-serif;
            text-transform: uppercase;
            transition: 0.2s;
        }
        .input-group button:hover { background: #fff; box-shadow: 0 0 20px #fff; }

        /* --- Animations --- */
        @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    </style>
</head>
<body>
    <div class="grid"></div>
    <div class="scanline"></div>

    <div class="hud-container">
        <!-- Top Bar -->
        <div class="top-info">
            <div class="logo">MK-LXXXV // JARVIS</div>
            <div class="status-txt">READY: <span id="status" style="color: #fff; text-shadow: 0 0 10px var(--glow-color);">CONNECTED</span></div>
        </div>

        <!-- Left Display -->
        <div class="panel side-panel" style="grid-column: 1;">
            <div class="side-metric">
                <span class="m-label">NEURAL NETWORK TRAFFIC</span>
                <div class="m-bar"><div class="m-fill" style="width: 82%;"></div></div>
            </div>
            <div class="side-metric">
                <span class="m-label">BIOMETRIC AUTHORIZATION</span>
                <div class="m-bar"><div class="m-fill" style="width: 98%;"></div></div>
            </div>
            <div class="code-stream" id="stream1">
                > INITIATING DUAL-CORE LINK...<br>
                > ACCESSING GLOBAL DATABANK...<br>
                > ENCRYPTION PROTOCOLS: ACTIVE<br>
                > TARGET: RAVI (MASTER)<br>
                > LOCATION: SERVER ROOM 1<br>
                > WIFI: 5G SECURE<br>
                > STATUS: NOMINAL<br>
            </div>
        </div>

        <!-- Center HUD (Hologram) -->
        <div class="center-hud">
            <div class="ring-container">
                <div class="ring ring-outer"></div>
                <div class="ring ring-mid"></div>
                <div class="ring ring-inner"></div>
                <div class="ring ring-core"></div>
                <div class="core" id="micBtn" onclick="toggleMic()">
                    <svg viewBox="0 0 24 24"><path d="M12 14c1.66 0 3-1.34 3-3V5c0-1.66-1.34-3-3-3S9 3.34 9 5v6c0 1.66 1.34 3 3 3z"/><path d="M17 11c0 2.76-2.24 5-5 5s-5-2.24-5-5H5c0 3.53 2.61 6.43 6 6.92V21h2v-3.08c3.39-.49 6-3.39 6-6.92h-2z"/></svg>
                </div>
            </div>
        </div>

        <!-- Right Display -->
        <div class="panel side-panel" style="grid-column: 3;">
            <div class="side-metric">
                <span class="m-label">CORE POWER CELL</span>
                <div class="m-bar"><div class="m-fill" style="width: 94%;"></div></div>
            </div>
            <div class="side-metric">
                <span class="m-label">SATELLITE DOWNLINK</span>
                <div class="m-bar"><div class="m-fill" style="width: 71%;"></div></div>
            </div>
            <div class="code-stream" id="stream2">
                [AI ENGINE: GROQ-LLAMA3-70B]<br>
                [VOICE RECOGNITION: ENABLED]<br>
                [LOCAL FS ACCESS: GRANTED]<br>
                [WEATHER: COLOMBO - CLEAR]<br>
                [TIME: 17:28:44]<br>
                [UPTIME: 12h 44m]<br>
                [READY FOR COMMANDS]<br>
            </div>
        </div>

        <!-- Interface -->
        <div class="panel chat-panel">
            <div class="chat-box" id="chat">
                <div class="msg jarvis">Systems online, Ravi. Looking forward to our next mission. What's the plan?</div>
            </div>
            <div class="input-group">
                <input type="text" id="userInput" placeholder="ENTER VOICE OR TEXT COMMAND..." onkeypress="if(event.key==='Enter')sendText()">
                <button onclick="sendText()">ACCESS</button>
            </div>
        </div>
    </div>

    <audio id="jarvisAudio" style="display:none"></audio>

    <script>
        const chat = document.getElementById('chat');
        const audio = document.getElementById('jarvisAudio');
        let isListening = false;
        let isSpeaking = false;

        // ─── SSE: Real-time feed from server ────────────────────────────────
        // Connects once on load. Server pushes messages from wake-word listener,
        // Telegram, or text input — all appear here instantly.
        function connectSSE() {
            const es = new EventSource('/events');
            es.onmessage = (e) => {
                const data = JSON.parse(e.data);
                if (data.role === 'jarvis') {
                    addMsg(data.text, 'jarvis');
                    playVoice(data.text);
                } else if (data.role === 'user') {
                    addMsg(data.text, 'user');
                }
                // 'system' events (e.g. 'SSE stream connected') are silent
            };
            es.onerror = () => {
                // Auto-reconnect after 3s
                es.close();
                setTimeout(connectSSE, 3000);
            };
        }
        connectSSE();

        // ─── Web Speech API (browser mic — Chrome/Edge only) ─────────────────
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        let recognition = null;
        if (SpeechRecognition) {
            recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onresult = (event) => {
                if (isSpeaking) return;
                let interim = '', final = '';
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) final += event.results[i][0].transcript;
                    else interim += event.results[i][0].transcript;
                }
                if (interim) document.getElementById('userInput').value = interim;
                if (final.trim()) {
                    document.getElementById('userInput').value = '';
                    sendQuery(final.trim());
                }
            };

            recognition.onerror = (e) => {
                if (e.error === 'not-allowed') {
                    addMsg('Browser mic permission denied. Open chrome://settings/content/microphone and allow localhost.', 'jarvis');
                    isListening = false;
                    document.getElementById('micBtn').classList.remove('recording');
                    setStatus('CONNECTED', '#fff');
                }
            };

            recognition.onend = () => {
                if (isListening && !isSpeaking) {
                    try { recognition.start(); } catch(e) {}
                }
            };
        }

        // ─── Helpers ─────────────────────────────────────────────────────────
        function addMsg(text, role) {
            const d = document.createElement('div');
            d.className = 'msg ' + role;
            d.textContent = (role === 'jarvis' ? 'JARVIS // ' : 'USER // ') + text.toUpperCase();
            chat.appendChild(d);
            chat.scrollTop = chat.scrollHeight;
        }

        function playVoice(replyText) {
            isSpeaking = true;
            if (recognition && isListening) try { recognition.stop(); } catch(e) {}
            fetch('/tts', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({text: replyText})
            }).then(r => r.blob()).then(blob => {
                audio.src = URL.createObjectURL(blob);
                audio.play();
                audio.onended = () => {
                    isSpeaking = false;
                    if (isListening) try { recognition.start(); } catch(e) {}
                    setStatus('LISTENING...', '#ff4444');
                };
            }).catch(() => { isSpeaking = false; });
        }

        // sendQuery: only used by browser text/speech input.
        // SSE handles display — so we DON'T call addMsg here (server will push it back via SSE).
        async function sendQuery(text) {
            if (!text) return;
            setStatus('ANALYZING...', '#ffcc00');
            try {
                await fetch('/ask', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: text})
                });
                // Response will come via SSE automatically
                setStatus(isListening ? 'LISTENING...' : 'CONNECTED', isListening ? '#ff4444' : '#fff');
            } catch(e) {
                setStatus('CONNECTED', '#fff');
            }
        }

        async function sendText() {
            const inp = document.getElementById('userInput');
            const text = inp.value.trim();
            if (!text) return;
            inp.value = '';
            await sendQuery(text);
        }

        function setStatus(text, color) {
            const s = document.getElementById('status');
            s.textContent = text;
            s.style.color = color;
        }

        // ─── Mic Button: toggle always-on browser speech ──────────────────────
        function toggleMic() {
            const btn = document.getElementById('micBtn');
            if (!SpeechRecognition) {
                addMsg('Real-time speech requires Chrome or Edge browser.', 'jarvis');
                return;
            }
            if (!isListening) {
                recognition.start();
                isListening = true;
                btn.classList.add('recording');
                setStatus('LISTENING...', '#ff4444');
            } else {
                recognition.stop();
                isListening = false;
                btn.classList.remove('recording');
                setStatus('CONNECTED', '#fff');
            }
        }

        // ─── Live Holographic Log Generators ─────────────────────────────────
        const sysLogs = [
            "RECALIBRATING NEURAL MATRIX... [OK]",
            "SCANNING LOCAL THREATS: 0 FOUND",
            "SATELLITE UPLINK: STABLE",
            "ALLOCATING MEMORY BLOCKS... [DONE]",
            "ENCRYPTION KEY ROTATED EXTERNALLY",
            "BIOMETRIC MATCH: RAVI (VERIFIED)",
            "OPTIMIZING SUBROUTINES: 98%",
            "FIREWALL STATUS: SECURE",
            "SYNCING GLOBAL DATABANK",
            "DIAGNOSTIC CYCLE COMPLETE",
            "AEROSPACE TRACKING: INACTIVE",
            "THERMAL SIGNATURES: NOMINAL",
            "BYPASSING PROXY LAYERS..."
        ];

        setInterval(() => {
            const streams = ['stream1', 'stream2'];
            // Pick random left or right stream to update
            const targetStreamId = streams[Math.floor(Math.random() * streams.length)];
            const stream = document.getElementById(targetStreamId);
            if (!stream) return;

            // Extract lines
            let lines = stream.innerHTML.split('<br>');
            if (lines.length > 8) lines.shift(); // Keep limit to 8 lines to prevent scrolling off

            const time = new Date().toLocaleTimeString('en-US', {hour12: false});
            const msg = sysLogs[Math.floor(Math.random() * sysLogs.length)];
            
            // Make some logs have timestamps, others just system messages
            if (Math.random() > 0.4) {
                lines.push(`> [${time}] ${msg}`);
            } else {
                lines.push(`> ${msg}`);
            }

            stream.innerHTML = lines.join('<br>');
        }, 1200); // 1.2s intervals makes it look very active
    </script>
</body>
</html>
"""

@app.route('/')
def home():
    return DASHBOARD_HTML

@app.route('/ask', methods=['POST'])
def ask():
    data = request.get_json()
    query = data.get('query')
    history = load_memory()
    push_event('user', query)  # echo to SSE so all tabs see it
    reply = think(query, history)
    add_message(history, "user", query)
    add_message(history, "assistant", reply)
    push_event('jarvis', reply)  # push reply to SSE
    return jsonify({"reply": reply})

@app.route('/voice', methods=['POST'])
def voice():
    if 'audio' not in request.files:
        return jsonify({"reply": "No audio received."})
    audio = request.files['audio']
    with tempfile.NamedTemporaryFile(suffix=".webm", delete=False) as f:
        audio.save(f.name)
        path = f.name

    text = transcribe_audio(path)
    try: os.unlink(path)
    except: pass

    if not text:
        return jsonify({"reply": "I couldn't hear you clearly. Try again."})

    history = load_memory()
    push_event('user', text)
    reply = think(text, history)
    add_message(history, "user", text)
    add_message(history, "assistant", reply)
    push_event('jarvis', reply)
    return jsonify({"query": text, "reply": reply})

@app.route('/events')
def events():
    """Server-Sent Events endpoint: streams conversation events to browser."""
    def generate():
        yield 'data: {"role":"system","text":"SSE stream connected"}\n\n'
        while True:
            try:
                event = _event_queue.get(timeout=25)
                yield f'data: {json.dumps(event)}\n\n'
            except queue.Empty:
                yield ': heartbeat\n\n'  # keep connection alive
    return Response(generate(), mimetype='text/event-stream',
                    headers={'Cache-Control': 'no-cache', 'X-Accel-Buffering': 'no'})

@app.route('/tts', methods=['POST'])
def tts():
    """Generate neural TTS audio and send it to the browser for playback."""
    data = request.get_json()
    text = data.get('text', '')
    if not text:
        return "No text", 400

    audio_path = text_to_audio_file(text)
    if audio_path and os.path.exists(audio_path):
        return send_file(audio_path, mimetype='audio/mpeg')
    return "TTS failed", 500

def run_gui():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

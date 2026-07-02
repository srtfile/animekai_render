import requests
import re
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Safari/537.36",
    "Referer": "https://animekai.to/",
    "Accept": "application/json"
}

API = "https://enc-dec.app/api"
KAI_AJAX = "https://animekai.to/ajax"

HTML = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>AnimeKai Extractor</title>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { font-family: 'Segoe UI', sans-serif; background: #0f0f1a; color: #e0e0e0; min-height: 100vh; padding: 20px; }
  .container { max-width: 900px; margin: 0 auto; }
  h1 { text-align: center; color: #ff6b6b; margin-bottom: 8px; font-size: 2rem; }
  .subtitle { text-align: center; color: #888; margin-bottom: 30px; font-size: 0.9rem; }
  .card { background: #1a1a2e; border: 1px solid #2a2a4a; border-radius: 12px; padding: 24px; margin-bottom: 20px; }
  label { display: block; margin-bottom: 6px; color: #aaa; font-size: 0.85rem; text-transform: uppercase; letter-spacing: 0.05em; }
  input, select { width: 100%; padding: 10px 14px; background: #0f0f1a; border: 1px solid #3a3a5a; border-radius: 8px; color: #e0e0e0; font-size: 0.95rem; margin-bottom: 16px; outline: none; }
  input:focus, select:focus { border-color: #ff6b6b; }
  .row { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
  button { width: 100%; padding: 12px; background: #ff6b6b; color: white; border: none; border-radius: 8px; font-size: 1rem; font-weight: 600; cursor: pointer; transition: background 0.2s; }
  button:hover { background: #e05555; }
  button:disabled { background: #444; cursor: not-allowed; }
  .output { background: #0a0a15; border: 1px solid #2a2a4a; border-radius: 8px; padding: 16px; min-height: 120px; font-family: monospace; font-size: 0.85rem; white-space: pre-wrap; word-break: break-all; color: #a0f0a0; }
  .step { display: flex; align-items: center; gap: 10px; padding: 8px 0; border-bottom: 1px solid #2a2a4a; color: #888; font-size: 0.85rem; }
  .step:last-child { border-bottom: none; }
  .dot { width: 8px; height: 8px; border-radius: 50%; background: #444; flex-shrink: 0; }
  .step.done .dot { background: #4caf50; }
  .step.active .dot { background: #ff6b6b; animation: pulse 1s infinite; }
  .step.error .dot { background: #f44336; }
  @keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.3} }
  .badge { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; background: #2a2a4a; color: #ff6b6b; margin-left: 8px; }
  .error-msg { color: #f44336; }
</style>
</head>
<body>
<div class="container">
  <h1>🎌 AnimeKai</h1>
  <p class="subtitle">Extract decrypted stream data from animekai.to</p>
  <div class="card">
    <label>Content URL</label>
    <input type="text" id="url" value="https://animekai.to/watch/cyberpunk-edgerunners-x6qm" placeholder="https://animekai.to/watch/...">
    <div class="row">
      <div>
        <label>Season</label>
        <input type="text" id="season" value="1">
      </div>
      <div>
        <label>Episode</label>
        <input type="text" id="episode" value="1">
      </div>
    </div>
    <div class="row">
      <div>
        <label>Type</label>
        <select id="type">
          <option value="softsub">softsub</option>
          <option value="sub">sub</option>
          <option value="dub">dub</option>
        </select>
      </div>
      <div>
        <label>Server ID</label>
        <input type="text" id="server_id" value="1">
      </div>
    </div>
    <button id="runBtn" onclick="run()">▶ Extract Stream Data</button>
  </div>
  <div class="card">
    <label>Progress</label>
    <div id="steps">
      <div class="step" id="s1"><div class="dot"></div> Extract Content ID</div>
      <div class="step" id="s2"><div class="dot"></div> Fetch Episodes List</div>
      <div class="step" id="s3"><div class="dot"></div> Fetch Servers List</div>
      <div class="step" id="s4"><div class="dot"></div> Decrypt Stream Data</div>
    </div>
  </div>
  <div class="card">
    <label>Output <span class="badge" id="badge"></span></label>
    <div class="output" id="output">Results will appear here...</div>
  </div>
</div>
<script>
async function run() {
  const btn = document.getElementById('runBtn');
  btn.disabled = true;
  document.getElementById('output').textContent = 'Running...';
  document.getElementById('badge').textContent = '';
  ['s1','s2','s3','s4'].forEach(id => document.getElementById(id).className = 'step');
  try {
    const resp = await fetch('/run', {
      method: 'POST',
      headers: {'Content-Type':'application/json'},
      body: JSON.stringify({
        url: document.getElementById('url').value,
        season: document.getElementById('season').value,
        episode: document.getElementById('episode').value,
        type: document.getElementById('type').value,
        server_id: document.getElementById('server_id').value,
      })
    });
    const data = await resp.json();
    data.steps.forEach((s,i) => document.getElementById('s'+(i+1)).classList.add(s.status));
    if (data.error) {
      document.getElementById('output').innerHTML = '<span class="error-msg">ERROR: ' + data.error + '</span>';
      document.getElementById('badge').textContent = 'FAILED';
    } else {
      document.getElementById('output').textContent = JSON.stringify(data.result, null, 2);
      document.getElementById('badge').textContent = 'SUCCESS';
    }
  } catch(e) {
    document.getElementById('output').innerHTML = '<span class="error-msg">' + e.message + '</span>';
  }
  btn.disabled = false;
}
</script>
</body>
</html>'''

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/run', methods=['POST'])
def run():
    data = request.json
    url = data.get('url', '')
    season = data.get('season', '1')
    episode = data.get('episode', '1')
    srv_type = data.get('type', 'softsub')
    server_id = data.get('server_id', '1')
    steps = [{"label": "", "status": "active"}, {"label": "", "status": ""}, {"label": "", "status": ""}, {"label": "", "status": ""}]
    try:
        html = requests.get(url, headers=HEADERS, timeout=15).text
        m = re.search(r'<div[^>]*id="anime-rating"[^>]*data-id="([^"]+)"', html)
        if not m:
            steps[0]["status"] = "error"
            return jsonify({"steps": steps, "error": "Could not extract content ID"})
        content_id = m.group(1)
        steps[0]["status"] = "done"

        steps[1]["status"] = "active"
        enc_id = requests.get(f"{API}/enc-kai?text={content_id}", timeout=10).json()["result"]
        episodes_resp = requests.get(f"{KAI_AJAX}/episodes/list?ani_id={content_id}&_={enc_id}", headers=HEADERS, timeout=10).json()
        episodes = requests.post(f"{API}/parse-html", json={"text": episodes_resp["result"]}, timeout=10).json()["result"]
        steps[1]["status"] = "done"

        steps[2]["status"] = "active"
        token = episodes[season][episode]["token"]
        enc_token = requests.get(f"{API}/enc-kai?text={token}", timeout=10).json()["result"]
        servers_resp = requests.get(f"{KAI_AJAX}/links/list?token={token}&_={enc_token}", headers=HEADERS, timeout=10).json()
        servers = requests.post(f"{API}/parse-html", json={"text": servers_resp["result"]}, timeout=10).json()["result"]
        lid = servers[srv_type][server_id]["lid"]
        steps[2]["status"] = "done"

        steps[3]["status"] = "active"
        enc_lid = requests.get(f"{API}/enc-kai?text={lid}", timeout=10).json()["result"]
        embed_resp = requests.get(f"{KAI_AJAX}/links/view?id={lid}&_={enc_lid}", headers=HEADERS, timeout=10).json()
        encrypted = embed_resp["result"]
        decrypted = requests.post(f"{API}/dec-kai", json={"text": encrypted}, timeout=10).json()["result"]
        steps[3]["status"] = "done"

        return jsonify({"steps": steps, "result": decrypted})
    except Exception as e:
        for s in steps:
            if s["status"] == "active":
                s["status"] = "error"
        return jsonify({"steps": steps, "error": str(e)})

if __name__ == '__main__':
    import os
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))

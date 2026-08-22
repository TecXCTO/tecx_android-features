import subprocess
import json
import time
import os
import threading
from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

# --- CONFIGURATION ENGINE (Holds state for background loop and web UI) ---
CONFIG = {
    "low_limit": 20,
    "high_limit": 80,
    "mute_alarms": False,
    "current_level": 50,
    "status": "Unknown",
    "temperature": 0.0,
    "health": "Unknown",
    "last_notified_percentage": -1,
    "low_alarm_active": False,
    "high_alarm_active": False
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_ALARM_PATH = os.path.join(SCRIPT_DIR, "alarm.mp3")

# --- NATIVE TERMUX INTERACTION LAYER ---
def get_battery_status():
    """Queries the native Termux API binary layer directly."""
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"[Error] Failed to read hardware status: {e}")
        return None

def trigger_silent_update(level):
    """Sends low-priority notification cards and announces level shifts using TTS."""
    if CONFIG["mute_alarms"]:
        return
    title = "🔋 Battery Update"
    msg = f"Battery level is now at {level}%"
    subprocess.run(['termux-notification-remove', 'battery_update_id'], capture_output=True)
    subprocess.run(['termux-notification', '-i', 'battery_update_id', '-t', title, '-c', msg, '--priority', 'low'], capture_output=True)
    subprocess.run(['termux-tts-speak', f"Battery level is now {level} percent."], capture_output=True)

def trigger_critical_alarm(title, message):
    """Fires a persistent system alert card, shakes phone chassis, and loops audio targets."""
    if CONFIG["mute_alarms"]:
        return
    subprocess.run(['termux-toast', f"CRITICAL: {message}"], capture_output=True)
    subprocess.run(['termux-notification', '-i', 'battery_alarm_id', '-t', title, '-c', message, '--priority', 'high', '--ongoing'], capture_output=True)
    subprocess.run(['termux-vibrate', '-d', '500'], capture_output=True)
    
    if os.path.exists(CUSTOM_ALARM_PATH):
        check_player = subprocess.run(['termux-media-player', 'info'], capture_output=True, text=True)
        if "Playing" not in check_player.stdout:
            subprocess.run(['termux-media-player', 'play', CUSTOM_ALARM_PATH], capture_output=True)
    else:
        subprocess.run(['termux-tts-speak', message], capture_output=True)

def clear_critical_alarm():
    """Cleans up ongoing warning card states and cuts off trailing hardware player threads."""
    subprocess.run(['termux-notification-remove', 'battery_alarm_id'], capture_output=True)
    subprocess.run(['termux-media-player', 'stop'], capture_output=True)

# --- BACKGROUND HARDWARE MONITOR THREAD ---
def battery_monitor_loop():
    """Independent daemon loop validating rule parameters in background."""
    print("[Engine] Automated hardware tracking loops initialized successfully.")
    while True:
        status = get_battery_status()
        if status:
            CONFIG["current_level"] = status.get('percentage', CONFIG["current_level"])
            CONFIG["status"] = status.get('status', CONFIG["status"])
            CONFIG["temperature"] = status.get('temperature', CONFIG["temperature"])
            CONFIG["health"] = status.get('health', CONFIG["health"])
            
            level = CONFIG["current_level"]
            is_charging = (CONFIG["status"] == "CHARGING" or CONFIG["status"] == "FULL")

            # Condition 1: Low Boundary Alarm
            if level <= CONFIG["low_limit"] and not is_charging:
                CONFIG["high_alarm_active"] = False
                msg = f"Warning. Battery level dropped to {level} percent. Please plug in your charger."
                trigger_critical_alarm("🚨 Plug In Charger!", msg)
                CONFIG["low_alarm_active"] = True

            # Condition 2: High Boundary Alarm
            elif level >= CONFIG["high_limit"] and is_charging:
                CONFIG["low_alarm_active"] = False
                msg = f"Alert. Battery level reached {level} percent. Please unplug your charger."
                trigger_critical_alarm("🚨 Unplug Charger!", msg)
                CONFIG["high_alarm_active"] = True

            # Condition 3: Safe Mid-Range Granular Tracking Updates
            else:
                if CONFIG["low_alarm_active"] or CONFIG["high_alarm_active"]:
                    clear_critical_alarm()
                    CONFIG["low_alarm_active"] = False
                    CONFIG["high_alarm_active"] = False

                if level != CONFIG["last_notified_percentage"]:
                    if CONFIG["low_limit"] < level < CONFIG["high_limit"]:
                        trigger_silent_update(level)
                    CONFIG["last_notified_percentage"] = level
        
        time.sleep(5 if (CONFIG["low_alarm_active"] or CONFIG["high_alarm_active"]) else 15)

# --- WEB DASHBOARD FRONTEND HTML ---
DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>TecX Battery Pro Dashboard</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background-color: #121212; color: #e0e0e0; margin: 0; padding: 20px; display: flex; flex-direction: column; align-items: center; }
        .card { background-color: #1e1e1e; border-radius: 12px; padding: 20px; width: 100%; max-width: 400px; box-shadow: 0 4px 10px rgba(0,0,0,0.3); margin-bottom: 20px; text-align: center; }
        h1 { font-size: 22px; color: #ff9800; margin-top: 0; }
        .battery-display { font-size: 48px; font-weight: bold; margin: 15px 0; color: #4caf50; }
        .status-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; font-size: 14px; text-align: left; background: #262626; padding: 12px; border-radius: 8px; margin-bottom: 15px; }
        .form-group { margin: 15px 0; text-align: left; }
        label { display: block; font-size: 12px; color: #aaaaaa; margin-bottom: 5px; }
        input[type="number"] { width: 93%; padding: 10px; background: #2c2c2c; border: 1px solid #444; border-radius: 6px; color: #fff; font-size: 16px; }
        .btn { width: 100%; padding: 12px; background: #ff9800; border: none; border-radius: 6px; color: #121212; font-weight: bold; font-size: 16px; cursor: pointer; transition: background 0.2s; }
        .btn:hover { background: #e68a00; }
        .btn-mute { background: #333; color: #fff; margin-top: 10px; border: 1px solid #555; }
        .btn-muted { background: #f44336; color: #fff; }
    </style>
</head>
<body>

    <div class="card">
        <h1>🔋 TecX Battery Pro</h1>
        <div class="battery-display" id="bat-level">--%</div>
        
        <div class="status-grid">
            <div>State: <strong id="bat-status">--</strong></div>
            <div>Temp: <strong id="bat-temp">--°C</strong></div>
            <div>Health: <strong id="bat-health">--</strong></div>
            <div>Alarms: <strong id="alarm-state">OK</strong></div>
        </div>

        <button class="btn btn-mute" id="mute-btn" onclick="toggleMute()">Mute Audio Alerts</button>
    </div>

    <div class="card">
        <h3>Configuration Thresholds</h3>
        <div class="form-group">
            <label>Low Limit Boundary (%)</label>
            <input type="number" id="low-limit" min="1" max="40">
        </div>
        <div class="form-group">
            <label>High Limit Boundary (%)</label>
            <input type="number" id="high-limit" min="60" max="100">
        </div>
        <button class="btn" onclick="saveLimits()">Update Rules</button>
    </div>

    <script>
        function updateDashboard() {
            fetch('/api/status')
                .then(res => res.json())
                .then(data => {
                    document.getElementById('bat-level').innerText = data.current_level + '%';
                    document.getElementById('bat-status').innerText = data.status;
                    document.getElementById('bat-temp').innerText = data.temperature + '°C';
                    document.getElementById('bat-health').innerText = data.health;
                    
                    let alarmState = "OK";
                    if(data.low_alarm_active) alarmState = "CRITICAL LOW";
                    if(data.high_alarm_active) alarmState = "CRITICAL HIGH";
                    document.getElementById('alarm-state').innerText = alarmState;
                    document.getElementById('alarm-state').style.color = alarmState === "OK" ? "#4caf50" : "#f44336";

                    document.getElementById('low-limit').value = data.low_limit;
                    document.getElementById('high-limit').value = data.high_limit;

                    let muteBtn = document.getElementById('mute-btn');
                    if (data.mute_alarms) {
                        muteBtn.innerText = "🔇 Alerts Muted";
                        muteBtn.className = "btn btn-mute btn-muted";
                    } else {
                        muteBtn.innerText = "🔊 Alerts Enabled";
                        muteBtn.className = "btn btn-mute";
                    }
                });
        }

        function saveLimits() {
            let low = document.getElementById('low-limit').value;
            let high = document.getElementById('high-limit').value;
            fetch('/api/config', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ low_limit: parseInt(low), high_limit: parseInt(high) })
            }).then(() => alert("Configuration saved!"));
        }

        function toggleMute() {
            fetch('/api/mute', { method: 'POST' }).then(() => updateDashboard());
        }

        setInterval(updateDashboard, 3000);
updateDashboard();"""--- WEB ENDPOINTS REST API ---@app.route('/')def index():return render_template_string(DASHBOARD_HTML)@app.route('/api/status', methods=['GET'])def get_status():return jsonify(CONFIG)@app.route('/api/config', methods=['POST'])def set_config():data = request.jsonCONFIG["low_limit"] = data.get("low_limit", CONFIG["low_limit"])CONFIG["high_limit"] = data.get("high_limit", CONFIG["high_limit"])return jsonify({"status": "success"})@app.route('/api/mute', methods=['POST'])def toggle_mute():CONFIG["mute_alarms"] = not CONFIG["mute_alarms"]if CONFIG["mute_alarms"]:clear_critical_alarm()return jsonify({"status": "success"})if name == "main":# Start hardware checking runtime loops as a non-blocking daemon threadmonitor_thread = threading.Thread(target=battery_monitor_loop, daemon=True)monitor_thread.start()# Fire up local server deployment accessible via any web browser on the networkapp.run(host='0.0.0.0', port=5000, debug=False)
  

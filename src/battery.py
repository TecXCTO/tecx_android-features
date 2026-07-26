import subprocess
import json
import time

# --- CONFIGURATION ---
LOW_BATTERY_LEVEL = 20    # Alert to plug in when level is <= this
HIGH_BATTERY_LEVEL = 80   # Alert to unplug when level is >= this
CHECK_INTERVAL = 30       # Frequency of battery checks (in seconds)

def get_battery_status():
    """Queries the Termux API binary safely to get battery metrics."""
    try:
        # Runs the termux native command to get JSON data
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"Error fetching battery status: {e}")
        return None

def trigger_termux_alert(title, message):
    """Fires native Android alerts using the Termux environment."""
    # 1. Pop up a toast message on screen
    subprocess.run(['termux-toast', message])
    
    # 2. Fire a persistent Android tray notification
    subprocess.run(['termux-notification', '-t', title, '-c', message, '--priority', 'high'])
    
    # 3. Sound the alarm (Plays your system default ringtone notification)
    subprocess.run(['termux-tts-speak', message]) # Speaks the alert aloud as an audible alarm

def monitor_battery():
    print("Termux Battery monitoring active. Press Ctrl+C to terminate.")
    
    low_alert_triggered = False
    high_alert_triggered = False

    try:
        while True:
            status = get_battery_status()
            if not status:
                time.sleep(5)
                continue
            
            # Extract metrics from Termux JSON response
            level = status.get('percentage', -1)
            charging_state = status.get('status', 'DISCHARGING') # "CHARGING", "DISCHARGING", "FULL"
            is_charging = (charging_state == "CHARGING" or charging_state == "FULL")

            # --- CASE 1: Below or equal to low level AND discharging ---
            if level <= LOW_BATTERY_LEVEL and not is_charging:
                if not low_alert_triggered:
                    trigger_termux_alert("🔋 Battery Critical!", f"Battery level is {level}%. Please plug in!")
                    low_alert_triggered = True
            else:
                low_alert_triggered = False

            # --- CASE 2: Above or equal to high level AND charging ---
            if level >= HIGH_BATTERY_LEVEL and is_charging:
                if not high_alert_triggered:
                    trigger_termux_alert("⚡ Full Charge Alert!", f"Battery level is {level}%. Please unplug!")
                    high_alert_triggered = True
            else:
                high_alert_triggered = False

            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nMonitoring stopped manually.")

if __name__ == "__main__":
    monitor_battery()

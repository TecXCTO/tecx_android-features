import subprocess
import json
import time
import sys

def get_battery_status():
    """Queries the Termux API layer directly to grab current real-time statistics."""
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"\n[Error] Unable to contact Termux API: {e}")
        print("Please check that the 'Termux:API' app is installed from F-Droid.")
        return None

def trigger_silent_update(level):
    """Sends a quiet, non-vibrating notification for normal 1% changes."""
    title = "🔋 Battery Update"
    msg = f"Battery level is now at {level}%"
    # Remove previous dynamic updates to avoid cluttering the notification drawer
    subprocess.run(['termux-notification-remove', 'battery_update_id'], capture_output=True)
    # Post the fresh single status entry
    subprocess.run(['termux-notification', '-i', 'battery_update_id', '-t', title, '-c', msg, '--priority', 'low'], capture_output=True)

def trigger_critical_alarm(title, message):
    """Fires a high-priority persistent tray card, loops speech, and vibrates hardware."""
    # 1. Flash a brief floating toast across the screen
    subprocess.run(['termux-toast', f"CRITICAL: {message}"], capture_output=True)
    
    # 2. Push a persistent system notification card
    subprocess.run(['termux-notification', '-i', 'battery_alarm_id', '-t', title, '-c', message, '--priority', 'high', '--ongoing'], capture_output=True)
    
    # 3. Vibrate the physical phone chassis (Pattern: 500ms buzz, 250ms pause, repeated)
    subprocess.run(['termux-vibrate', '-d', '500'], capture_output=True)
    
    # 4. Sound the audible alarm by speaking the message aloud via the TTS engine
    subprocess.run(['termux-tts-speak', message], capture_output=True)

def clear_critical_alarm():
    """Cleans up and removes active critical alarm cards once boundaries clear."""
    subprocess.run(['termux-notification-remove', 'battery_alarm_id'], capture_output=True)

def main():
    print("=" * 45)
    print("   TERMUX CUSTOM CONFIGURABLE BATTERY MONITOR   ")
    print("=" * 45)

    # --- DYNAMIC USER CONFIGURATION RANGE INPUTS ---
    try:
        low_limit = int(input("Enter Custom Low Limit % (e.g., 1 to 40): ").strip())
        high_limit = int(input("Enter Custom High Limit % (e.g., 70 to 99): ").strip())
        
        if not (0 < low_limit < high_limit <= 100):
            print("[Error] Invalid ranges! Low limit must be smaller than high limit.")
            sys.exit(1)
            
    except ValueError:
        print("[Error] Please enter integer digits only.")
        sys.exit(1)

    print("\n[System] Initialization successful.")
    print(f"-> Critical Low Monitoring Bound: <= {low_limit}%")
    print(f"-> Safe Tracking Increments Zone: {low_limit + 1}% to {high_limit - 1}%")
    print(f"-> Critical High Monitoring Bound: >= {high_limit}%")
    print("Monitoring active... Press Ctrl+C to stop.\n")

    # State machine variables to block duplicate execution triggers
    last_notified_percentage = -1
    low_alarm_active = False
    high_alarm_active = False

    try:
        while True:
            status = get_battery_status()
            if not status:
                time.sleep(10)
                continue

            level = status.get('percentage', -1)
            charging_state = status.get('status', 'DISCHARGING') # "CHARGING", "DISCHARGING", "FULL"
            is_charging = (charging_state == "CHARGING" or charging_state == "FULL")

            if level == -1:
                time.sleep(5)
                continue

            # === ZONE 1: CRITICAL LOW RANGE BOUNDARY (Alarm + Vibrate) ===
            if level <= low_limit and not is_charging:
                high_alarm_active = False
                # Continues ringing/vibrating systematically on every loop while condition holds true
                msg = f"Battery is critically low at {level} percent! Please plug in the charger immediately."
                trigger_critical_alarm("🚨 Plug In Charger!", msg)
                low_alarm_active = True

            # === ZONE 2: CRITICAL HIGH RANGE BOUNDARY (Alarm + Vibrate) ===
            elif level >= high_limit and is_charging:
                low_alarm_active = False
                # Continues ringing/vibrating systematically on every loop while condition holds true
                msg = f"Battery is fully charged at {level} percent! Please unplug the charger now."
                trigger_critical_alarm("🚨 Unplug Charger!", msg)
                high_alarm_active = True

            # === ZONE 3: SAFE INTERMEDIATE ZONE (1% Incremental Silent Text Updates Only) ===
            else:
                # If an alarm was ringing but the user plugged/unplugged to fix it, clear the alarm
                if low_alarm_active or high_alarm_active:
                    clear_critical_alarm()
                    low_alarm_active = False
                    high_alarm_active = False

                # Handle granular notifications inside your dynamic mid-tier spectrum (e.g. 41%, 42%)
                if level != last_notified_percentage:
                    trigger_silent_update(level)
                    print(f"[Update] Battery changed to: {level}%")
                    last_notified_percentage = level

            # Evaluation check interval: Runs fast (every 4 seconds) when a boundary alert is ringing
            # so vibration loops effectively, otherwise sleeps to protect phone idle resources.
            if low_alarm_active or high_alarm_active:
                time.sleep(4)
            else:
                time.sleep(15)

    except KeyboardInterrupt:
        print("\n[System] Terminating session processes...")
        clear_critical_alarm()
        subprocess.run(['termux-notification-remove', 'battery_update_id'], capture_output=True)
        print("[System] Background battery monitor engine deactivated cleanly.")

if __name__ == "__main__":
    main()
      

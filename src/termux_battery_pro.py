import subprocess
import json
import time
import sys
import os

# Identify where the script is located to target the custom MP3 file path
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CUSTOM_ALARM_PATH = os.path.join(SCRIPT_DIR, "alarm.mp3")

def get_battery_status():
    """Queries the Termux API layer directly to grab current real-time statistics."""
    try:
        result = subprocess.run(['termux-battery-status'], capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        print(f"\n[Error] Unable to contact Termux API: {e}")
        return None

def speak_english_sentence(level):
    """Speaks a natural English sentence aloud via the Termux TTS engine."""
    # Custom sentence structure for the 1% mid-range shifts
    sentence = f"Battery level is now {level} percent."
    subprocess.run(['termux-tts-speak', sentence], capture_output=True)

def trigger_silent_update(level):
    """Sends a quiet text notification card and reads out the percentage shift in English."""
    title = "🔋 Battery Update"
    msg = f"Battery level is now at {level}%"
    
    # Update the notification center
    subprocess.run(['termux-notification-remove', 'battery_update_id'], capture_output=True)
    subprocess.run(['termux-notification', '-i', 'battery_update_id', '-t', title, '-c', msg, '--priority', 'low'], capture_output=True)
    
    # Speak the English tracking sentence
    speak_english_sentence(level)

def trigger_critical_alarm(title, message):
    """Fires a persistent tray card, loops your audio profile, and vibrates hardware."""
    # 1. Flash a brief floating toast across the screen
    subprocess.run(['termux-toast', f"CRITICAL: {message}"], capture_output=True)
    
    # 2. Push a persistent ongoing system notification card
    subprocess.run(['termux-notification', '-i', 'battery_alarm_id', '-t', title, '-c', message, '--priority', 'high', '--ongoing'], capture_output=True)
    
    # 3. Vibrate the physical phone chassis for 500ms
    subprocess.run(['termux-vibrate', '-d', '500'], capture_output=True)
    
    # 4. Audio Control Strategy: Custom MP3 vs Default System Alarm Fallback
    if os.path.exists(CUSTOM_ALARM_PATH):
        # Checks if media player is already running to prevent overlap glitching
        check_player = subprocess.run(['termux-media-player', 'info'], capture_output=True, text=True)
        if "Playing" not in check_player.stdout:
            # Play your custom tracking file completely offline
            subprocess.run(['termux-media-player', 'play', CUSTOM_ALARM_PATH], capture_output=True)
    else:
        # Fallback to speaking out the warning via TTS if no MP3 file is supplied
        subprocess.run(['termux-tts-speak', message], capture_output=True)

def clear_critical_alarm():
    """Cleans up active critical alarm tracking states and cuts off audio playback."""
    subprocess.run(['termux-notification-remove', 'battery_alarm_id'], capture_output=True)
    # Stop the custom MP3 playback if it's currently looping
    subprocess.run(['termux-media-player', 'stop'], capture_output=True)

def main():
    print("=" * 45)
    print("   TERMUX CUSTOM RECONFIGURABLE BATTERY PRO    ")
    print("=" * 45)

    # --- USER DYNAMIC LEVEL CONFIGURATION RANGE INPUTS ---
    try:
        low_limit = int(input("Enter Custom Low Limit % (e.g., 1 to 40): ").strip())
        high_limit = int(input("Enter Custom High Limit % (e.g., 70 to 99): ").strip())
        
        if not (0 < low_limit < high_limit <= 100):
            print("[Error] Invalid ranges! Low limit must be smaller than high limit.")
            sys.exit(1)
            
    except ValueError:
        print("[Error] Please enter integer digits only.")
        sys.exit(1)

    print(f"\n[System] Audio configuration initialized.")
    if os.path.exists(CUSTOM_ALARM_PATH):
        print("-> Custom Audio Profile: Loaded 'alarm.mp3' successfully.")
    else:
        print("-> Custom Audio Profile: Not found. Defaulting to system speech notifications.")
        
    print(f"-> Critical Low Boundary Alert: <= {low_limit}%")
    print(f"-> Mid-Range Spoken Tracking English Zone: {low_limit + 1}% to {high_limit - 1}%")
    print(f"-> Critical High Boundary Alert: >= {high_limit}%")
    print("Monitoring active... Press Ctrl+C to terminate.\n")

    # State machine tokens to prevent prompt spamming loop states
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
            charging_state = status.get('status', 'DISCHARGING') 
            is_charging = (charging_state == "CHARGING" or charging_state == "FULL")

            if level == -1:
                time.sleep(5)
                continue

            # === ZONE 1: CRITICAL LOW RANGE BOUNDARY (Alarm + Vibrate) ===
            if level <= low_limit and not is_charging:
                high_alarm_active = False
                msg = f"Warning. Battery level dropped to {level} percent at {time.strftime("%H:%M:%S")}. Please plug in your charger."
                trigger_critical_alarm("🚨 Plug In Charger!", msg)
                low_alarm_active = True

            # === ZONE 2: CRITICAL HIGH RANGE BOUNDARY (Alarm + Vibrate) ===
            elif level >= high_limit and is_charging:
                low_alarm_active = False
                msg = f"Alert. Battery level reached {level} percent at {time.strftime("%H:%M:%S")}. Please unplug your charger."
                trigger_critical_alarm("🚨 Unplug Charger!", msg)
                high_alarm_active = True

            # === ZONE 3: SAFE INTERMEDIATE ZONE (1% Incremental Silent Text Updates + English TTS) ===
            else:
                # If an alarm was ringing but the boundaries were resolved, clear execution instances
                if low_alarm_active or high_alarm_active:
                    clear_critical_alarm()
                    low_alarm_active = False
                    high_alarm_active = False

                # Handle granular notifications inside your dynamic mid-tier spectrum (e.g. 71% to 70%)
                if level != last_notified_percentage:
                    trigger_silent_update(level)
                    print(f"[Update] Spoken Alert Fired: Battery level is {level}% at {time.strftime("%H:%M:%S")} ")
                    last_notified_percentage = level

            # Speed up loops if alarms are active to repeat vibration effectively, otherwise save resources
            if low_alarm_active or high_alarm_active:
                time.sleep(5)
            else:
                time.sleep(15)

    except KeyboardInterrupt:
        print("\n[System] Terminating session processes...")
        clear_critical_alarm()
        subprocess.run(['termux-notification-remove', 'battery_update_id'], capture_output=True)
        print("[System] Background battery monitor engine deactivated cleanly.")

if __name__ == "__main__":
    main()
          

import androidhelper
import time

# --- CONFIGURATION ---
# Set your target battery percentages here
LOW_BATTERY_LEVEL = 20    # Alert to plug in when level is <= this
HIGH_BATTERY_LEVEL = 80   # Alert to unplug when level is >= this

# Frequency of battery checks (in seconds)
CHECK_INTERVAL = 30       

def monitor_battery():
    # Initialize the Android API bridge
    droid = androidhelper.Android()
    
    # Start tracking battery status
    droid.batteryStartMonitoring()
    print("Battery monitoring started. Press Ctrl+C in terminal to stop.")
    
    # Track states to prevent the alarm from spamming repeatedly
    low_alert_triggered = False
    high_alert_triggered = False

    try:
        while True:
            # Get current battery status
            status = droid.batteryGetStatus().result
            
            # Extract status data (returns -1 if failed)
            level = status.get('level', -1)
            plugged = status.get('plugged', -1)  # 0 = unplugged, 1+ = plugged into AC/USB
            
            if level == -1:
                print("Failed to read battery status. Retrying...")
                time.sleep(5)
                continue

            is_charging = plugged > 0

            # --- CASE 1: Below or equal to low level AND discharging ---
            if level <= LOW_BATTERY_LEVEL and not is_charging:
                if not low_alert_triggered:
                    title = "🔋 Battery Critical!"
                    message = f"Battery level is {level}%. Please plug in the charger!"
                    
                    droid.makeToast(message)
                    droid.notify(title, message)
                    droid.generateDstRingTone() # Generates default notification/alarm chime
                    
                    low_alert_triggered = True
                    print(f"[ALERT] Low battery: {level}%")
            else:
                # Reset state if battery goes above threshold or is plugged in
                low_alert_triggered = False

            # --- CASE 2: Above or equal to high level AND charging ---
            if level >= HIGH_BATTERY_LEVEL and is_charging:
                if not high_alert_triggered:
                    title = "⚡ Full Charge Alert!"
                    message = f"Battery level is {level}%. Please unplug the charger!"
                    
                    droid.makeToast(message)
                    droid.notify(title, message)
                    droid.generateDstRingTone() 
                    
                    high_alert_triggered = True
                    print(f"[ALERT] High battery: {level}%")
            else:
                # Reset state if battery drops below threshold or is unplugged
                high_alert_triggered = False

            # Wait before checking again to preserve battery life
            time.sleep(CHECK_INTERVAL)

    except KeyboardInterrupt:
        print("\nStopping monitor...")
    finally:
        # Clean up and stop the battery listener
        droid.batteryStopMonitoring()
        print("Monitoring stopped.")

if __name__ == "__main__":
    monitor_battery()
    

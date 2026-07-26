import androidhelper
import time
import os
from threading import Thread

# Kivy UI Components
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.core.audio import SoundLoader

class BatteryMonitorApp(App):
    def build(self):
        # Default Configurations
        self.low_limit = 20
        self.high_limit = 80
        self.is_running = False
        self.monitor_thread = None
        self.droid = androidhelper.Android()
        
        # Audio File setup (Looks for alarm.mp3 in the script directory)
        self.sound_path = os.path.join(os.path.dirname(__file__), "alarm.mp3")
        self.alarm_sound = None
        if os.path.exists(self.sound_path):
            self.alarm_sound = SoundLoader.load(self.sound_path)
            if self.alarm_sound:
                self.alarm_sound.loop = True  # Loop alarm until stopped

        # State tracking variables
        self.low_alert_triggered = False
        self.high_alert_triggered = False
        self.last_notified_percentage = -1 

        # Setup Graphical Interface Layout
        layout = BoxLayout(orientation='vertical', padding=30, spacing=20)
        
        # Title & Status Displayer
        self.status_label = Label(text="Status: Monitor Idle", font_size='20sp', size_hint_y=None, height=50)
        layout.add_widget(self.status_label)
        
        self.battery_label = Label(text="Current Battery: --%", font_size='32sp', bold=True)
        layout.add_widget(self.battery_label)

        # Inputs for custom thresholds
        layout.add_widget(Label(text="Low Battery Limit (Plug in %):", size_hint_y=None, height=30))
        self.low_input = TextInput(text="20", input_filter="int", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.low_input)

        layout.add_widget(Label(text="High Battery Limit (Unplug %):", size_hint_y=None, height=30))
        self.high_input = TextInput(text="80", input_filter="int", multiline=False, size_hint_y=None, height=50)
        layout.add_widget(self.high_input)

        # Engine Control Toggle Button
        self.toggle_btn = ToggleButton(text="START MONITOR", font_size='18sp', size_hint_y=None, height=60)
        self.toggle_btn.bind(on_press=self.toggle_monitor)
        layout.add_widget(self.toggle_btn)

        # Schedule dynamic screen update tick (Every 3 seconds)
        Clock.schedule_interval(self.update_ui, 3)
        
        return layout

    def toggle_monitor(self, instance):
        if instance.state == 'down':
            # Parse limits safely
            self.low_limit = int(self.low_input.text or 20)
            self.high_limit = int(self.high_input.text or 80)
            
            instance.text = "STOP MONITOR"
            self.status_label.text = "Status: Monitoring Active"
            self.is_running = True
            
            # Fire separate thread so UI does not freeze
            self.droid.batteryStartMonitoring()
            self.monitor_thread = Thread(target=self.background_logic)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()
        else:
            self.stop_engine(instance)

    def stop_engine(self, instance=None):
        self.is_running = False
        if self.toggle_btn:
            self.toggle_btn.text = "START MONITOR"
            self.toggle_btn.state = 'normal'
        self.status_label.text = "Status: Monitor Stopped"
        self.droid.batteryStopMonitoring()
        self.stop_alarm()

    def update_ui(self, dt):
        """Ticks synchronously to grab hardware status and show it on Screen."""
        if not self.is_running:
            return
        try:
            status = self.droid.batteryGetStatus().result
            level = status.get('level', -1)
            if level != -1:
                self.battery_label.text = f"Current Battery: {level}%"
        except Exception:
            pass

    def play_alarm(self):
        """Plays custom MP3 file if found, falls back to default if missing."""
        if self.alarm_sound:
            if self.alarm_sound.state != 'play':
                self.alarm_sound.play()
        else:
            # Fallback to system default notification chime if MP3 is absent
            self.droid.generateDstRingTone()

    def stop_alarm(self):
        if self.alarm_sound and self.alarm_sound.state == 'play':
            self.alarm_sound.stop()

    def background_logic(self):
        """Asynchronous worker loops here to verify threshold parameters continuously."""
        while self.is_running:
            try:
                status = self.droid.batteryGetStatus().result
                level = status.get('level', -1)
                plugged = status.get('plugged', -1)
                is_charging = plugged > 0

                if level == -1:
                    time.sleep(2)
                    continue

                # --- 1% GRANULAR PROGRESS NOTIFICATION FEATURE ---
                # Fires whenever level shifts by exactly 1% step inside active monitoring scope
                if level != self.last_notified_percentage:
                    title = "🔋 Battery Update"
                    msg = f"Battery level has changed to {level}%"
                    self.droid.notify(title, msg)
                    self.last_notified_percentage = level

                # --- CASE 1: Low critical reached & discharging ---
                if level <= self.low_limit and not is_charging:
                    if not self.low_alert_triggered:
                        self.droid.makeToast("CRITICAL LOW BATTERY!")
                        self.droid.notify("🔋 Plug in Charger!", f"Level dropped to {level}%")
                        self.play_alarm()
                        self.low_alert_triggered = True
                else:
                    if not is_charging: 
                        # Turn off alarm tone if user plugs charger in
                        self.stop_alarm()
                    self.low_alert_triggered = False

                # --- CASE 2: High threshold reached & charging ---
                if level >= self.high_limit and is_charging:
                    if not self.high_alert_triggered:
                        self.droid.makeToast("BATTERY FULLY CHARGED!")
                        self.droid.notify("⚡ Unplug Charger!", f"Level reached {level}%")
                        self.play_alarm()
                        self.high_alert_triggered = True
                else:
                    if is_charging:
                        # Turn off alarm tone if user unplugs charger
                        self.stop_alarm()
                    self.high_alert_triggered = False

            except Exception as e:
                print(f"Error in background task loop: {e}")

            time.sleep(5) # Evaluates states every 5 seconds to reduce CPU wear

    def on_stop(self):
        self.stop_engine()

if __name__ == "__main__":
    BatteryMonitorApp().run()

package com.example.batterymonitor

import android.app.*
import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.media.RingtoneManager
import android.os.BatteryManager
import android.os.Build
import android.os.IBinder
import androidx.core.app.NotificationCompat

class BatteryMonitorService : Service() {

    private val CHANNEL_ID = "battery_monitor_service_channel"
    private val ALERT_CHANNEL_ID = "battery_alerts_channel"

    private var lowAlertTriggered = false
    private var highAlertTriggered = false

    private val batteryReceiver = object : BroadcastReceiver() {
        override fun onReceive(context: Context, intent: Intent) {
            if (intent.action == Intent.ACTION_BATTERY_CHANGED) {
                val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
                val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
                val pct = (level / scale.toFloat() * 100).toInt()

                val status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
                val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || 
                                 status == BatteryManager.BATTERY_STATUS_FULL

                // DYNAMIC FETCH: Pull updated limits configured by user in the UI
                val sharedPrefs = context.getSharedPreferences("BatteryMonitorPrefs", Context.MODE_PRIVATE)
                val lowThreshold = sharedPrefs.getInt("low_limit", 20)
                val highThreshold = sharedPrefs.getInt("high_limit", 80)

                // Condition 1: Low Battery Alert
                if (pct <= lowThreshold && !isCharging) {
                    if (!lowAlertTriggered) {
                        triggerAlarmNotification(context, "🔋 Battery Critical!", "Level is $pct%. Plug in your charger!")
                        lowAlertTriggered = true
                    }
                } else { lowAlertTriggered = false }

                // Condition 2: High Battery Alert
                if (pct >= highThreshold && isCharging) {
                    if (!highAlertTriggered) {
                        triggerAlarmNotification(context, "⚡ Fully Charged!", "Level is $pct%. Unplug your charger!")
                        highAlertTriggered = true
                    }
                } else { highAlertTriggered = false }
            }
        }
    }

    override fun onCreate() {
        super.onCreate()
        createNotificationChannels()
        
        val statusNotification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Battery Monitor Active")
            .setContentText("Monitoring custom limits in background.")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .setPriority(NotificationCompat.PRIORITY_LOW)
            .setOngoing(true)
            .build()

        startForeground(1, statusNotification)

        val filter = IntentFilter(Intent.ACTION_BATTERY_CHANGED)
        registerReceiver(batteryReceiver, filter)
    }

    private fun triggerAlarmNotification(context: Context, title: String, message: String) {
        val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)

        val alert = NotificationCompat.Builder(context, ALERT_CHANNEL_ID)
            .setSmallIcon(android.R.drawable.ic_lock_idle_low_battery)
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setSound(alarmSound)
            .setAutoCancel(true)
            .build()

        manager.notify(102, alert)
    }

    private fun createNotificationChannels() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val manager = getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
            val serviceChannel = NotificationChannel(CHANNEL_ID, "Background Service", NotificationManager.IMPORTANCE_LOW)
            val alertChannel = NotificationChannel(ALERT_CHANNEL_ID, "Battery Alarm Alerts", NotificationManager.IMPORTANCE_HIGH)
            manager.createNotificationChannel(serviceChannel)
            manager.createNotificationChannel(alertChannel)
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int = START_STICKY
    override fun onDestroy() {
        super.onDestroy()
        unregisterReceiver(batteryReceiver)
    }
    override fun onBind(intent: Intent?): IBinder? = null
}

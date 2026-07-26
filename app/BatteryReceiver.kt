import android.content.BroadcastReceiver
import android.content.Context
import android.content.Intent
import android.os.BatteryManager
import android.media.RingtoneManager
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import androidx.core.app.NotificationCompat

class BatteryReceiver : BroadcastReceiver() {

    // Define your thresholds here
    private val LOW_BATTERY_THRESHOLD = 20
    private val HIGH_BATTERY_THRESHOLD = 80

    override fun onReceive(context: Context, intent: Intent) {
        if (intent.action == Intent.ACTION_BATTERY_CHANGED) {
            
            // Get current battery level
            val level = intent.getIntExtra(BatteryManager.EXTRA_LEVEL, -1)
            val scale = intent.getIntExtra(BatteryManager.EXTRA_SCALE, -1)
            val batteryPct = (level / scale.toFloat() * 100).toInt()

            // Get charging status
            val status = intent.getIntExtra(BatteryManager.EXTRA_STATUS, -1)
            val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || 
                             status == BatteryManager.BATTERY_STATUS_FULL

            // Condition 1: Low battery and discharging
            if (batteryPct <= LOW_BATTERY_THRESHOLD && !isCharging) {
                triggerAlert(context, "Battery Low ($batteryPct%)", "Please plug in your charger!")
            }
            
            // Condition 2: High battery and charging
            else if (batteryPct >= HIGH_BATTERY_THRESHOLD && isCharging) {
                triggerAlert(context, "Battery Charged ($batteryPct%)", "Please unplug your charger!")
            }
        }
    }

    private fun triggerAlert(context: Context, title: String, message: String) {
        val channelId = "battery_alerts"
        val notificationManager = context.getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager

        // Create Notification Channel for Android 8.0+
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val channel = NotificationChannel(channelId, "Battery Alerts", NotificationManager.IMPORTANCE_HIGH)
            notificationManager.createNotificationChannel(channel)
        }

        // Get default alarm sound URI
        val alarmSound = RingtoneManager.getDefaultUri(RingtoneManager.TYPE_ALARM)

        // Build notification
        val builder = NotificationCompat.Builder(context, channelId)
            .setSmallIcon(android.R.drawable.ic_lock_idle_low_battery) // Replace with your icon
            .setContentTitle(title)
            .setContentText(message)
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setSound(alarmSound) // This plays the alarm sound
            .setAutoCancel(true)

        // Fire notification
        notificationManager.notify(101, builder.build())
    }
}

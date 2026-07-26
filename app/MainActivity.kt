package com.example.batterymonitor

import android.Manifest
import android.content.Context
import android.content.Intent
import android.content.pm.PackageManager
import android.os.Build
import android.os.Bundle
import android.widget.Button
import android.widget.EditText
import android.widget.Toast
import androidx.activity.result.contract.ActivityResultContracts
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.ContextCompat
import com.google.android.material.materialswitch.MaterialSwitch

class MainActivity : AppCompatActivity() {

    private lateinit var switchService: MaterialSwitch
    private lateinit var etLowLimit: EditText
    private lateinit var etHighLimit: EditText
    private lateinit var btnSave: Button

    private val requestPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { isGranted: Boolean ->
        if (isGranted) {
            handleServiceStart()
        } else {
            switchService.isChecked = false
            Toast.makeText(this, "Notification permission required for battery alerts!", Toast.LENGTH_LONG).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI Elements
        switchService = findViewById(R.id.switchService)
        etLowLimit = findViewById(R.id.etLowLimit)
        etHighLimit = findViewById(R.id.etHighLimit)
        btnSave = findViewById(R.id.btnSave)

        val sharedPrefs = getSharedPreferences("BatteryMonitorPrefs", Context.MODE_PRIVATE)

        // Load Saved Configuration States
        etLowLimit.setText(sharedPrefs.getInt("low_limit", 20).toString())
        etHighLimit.setText(sharedPrefs.getInt("high_limit", 80).toString())
        switchService.isChecked = sharedPrefs.getBoolean("service_enabled", false)

        // Switch Toggle Listener Logic
        switchService.setOnCheckedChangeListener { _, isChecked ->
            sharedPrefs.edit().putBoolean("service_enabled", isChecked).apply()
            if (isChecked) {
                checkPermissionsAndProceed()
            } else {
                stopBatteryService()
            }
        }

        // Limit Saver Listener Logic
        btnSave.setOnClickListener {
            val lowVal = etLowLimit.text.toString().toIntOrNull() ?: 20
            val highVal = etHighLimit.text.toString().toIntOrNull() ?: 80

            if (lowVal in 1..99 && highVal in 1..100 && lowVal < highVal) {
                sharedPrefs.edit().putInt("low_limit", lowVal).putInt("high_limit", highVal).apply()
                Toast.makeText(this, "Limits saved successfully!", Toast.LENGTH_SHORT).show()
            } else {
                Toast.makeText(this, "Invalid inputs! Ensure low limit is less than high limit.", Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun checkPermissionsAndProceed() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.TIRAMISU) {
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED) {
                handleServiceStart()
            } else {
                requestPermissionLauncher.launch(Manifest.permission.POST_NOTIFICATIONS)
            }
        } else {
            handleServiceStart()
        }
    }

    private fun handleServiceStart() {
        val serviceIntent = Intent(this, BatteryMonitorService::class.java)
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
    }

    private fun stopBatteryService() {
        stopService(Intent(this, BatteryMonitorService::class.java))
        Toast.makeText(this, "Battery monitor stopped.", Toast.LENGTH_SHORT).show()
    }
}

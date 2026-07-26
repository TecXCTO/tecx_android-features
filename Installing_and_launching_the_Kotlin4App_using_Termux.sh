# Install your App APK via Termux
adb install /sdcard/Download/app-debug.apk
# Start the App completely via Termux Command Line
adb shell am start -n com.example.batterymonitor/.MainActivity
# adb shell am start -n ai.tecx.batterymonitor/.MainActivity
# Test it live
# Force low battery state to test the app's response
adb shell dumpsys battery set usb 0
adb shell dumpsys battery set status 3
adb shell dumpsys battery set level 12

# Your Kotlin app will instantly play the custom alarm pattern and trigger the hardware vibration engine you programmed.
# Once your testing looks good, remember to clear the mock environment using 

adb shell dumpsys battery reset

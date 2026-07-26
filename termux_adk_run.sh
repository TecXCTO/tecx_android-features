# pkg update && pkg upgrade -y
pkg install android-tools -y
# To verify the installation succeeded
adb version
# Pair Termux with Your Device
adb pair 192.168.1.5:43215
# Connect ADB to Your Phone
adb connect 192.168.1.5:37859
adb devices
# Execute Battery Mock Commands

# 1. Unhook physical power status
adb shell dumpsys battery set usb 0

# 2. Fake low battery (Triggers your Pydroid or Kotlin low alarm)
adb shell dumpsys battery set status 3
adb shell dumpsys battery set level 15

# 3. Fake high battery while charging (Triggers full charge unplug alert)
adb shell dumpsys battery set status 2
adb shell dumpsys battery set level 95

# 4. Clean up and restore actual system reporting
adb shell dumpsys battery reset

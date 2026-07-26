# Setup Phase
adb shell dumpsys battery set usb 0
# Test the Low Battery Alarm (Plug In Alert)
adb shell dumpsys battery set status 3
adb shell dumpsys battery set level 15
# Test the High Battery Alarm (Unplug Alert)
adb shell dumpsys battery set status 2
adb shell dumpsys battery set level 95
# Reset Phase (Crucial)
adb shell dumpsys battery reset

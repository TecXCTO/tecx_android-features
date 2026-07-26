# Install Java and Android Build Tools in Termux

# pkg update && pkg upgrade -y
pkg install git openjdk-17 tur-repo -y
pkg install android-sdk -y

# Clone Your GitHub Repository
# git clone https://github.com
# cd YOUR_REPO_NAME

# Compile the Source Code into an APK
chmod +x gradlew
./gradlew assembleDebug

# Install the Built App via ADB
adb install app/build/outputs/apk/debug/app-debug.apk

# Method 2: Use GitHub Actions (Easiest & Fastest)

# Download and Install the APK via Termux
termux-setup-storage
adb install /sdcard/Download/app-debug.apk
# Launch and Test Your App
adb shell am start -n com.example.batterymonitor/.MainActivity
# adb shell am start -n ai.tecx.batterymonitor/.MainActivity

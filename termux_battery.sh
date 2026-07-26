# pkg update && pkg upgrade -y
pkg install python termux-api coreutils -y
pip install termux-api
python src/termux_battery.py

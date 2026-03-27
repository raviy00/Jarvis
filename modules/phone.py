# modules/phone.py - ADB Control for Jarvis
import os
import subprocess
import time

def run_adb(command):
    """Run an ADB command and return output."""
    try:
        cmd = f"adb {command}"
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return result.stdout.strip()
    except Exception as e:
        return f"❌ ADB error: {e}"

def is_device_connected():
    """Check if any device is connected via ADB."""
    res = run_adb("devices")
    lines = res.split('\n')
    return len(lines) > 1 and "device" in lines[1]

def send_whatsapp(number, message):
    """Send a WhatsApp message via ADB (requires WhatsApp open on phone)."""
    if not is_device_connected():
        return "❌ No Android device detected via ADB. Connect your phone!"
        
    try:
        # 1. Open WhatsApp to a specific contact
        # am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone=NUMBER"
        run_adb(f'shell am start -a android.intent.action.VIEW -d "https://api.whatsapp.com/send?phone={number}"')
        time.sleep(2) # Wait for app to open
        
        # 2. Type the message
        # Convert spaces to %s for adb shell input text (standard)
        safe_msg = message.replace(" ", "%s")
        run_adb(f'shell input text "{safe_msg}"')
        
        # 3. Press the Send button (usually at a specific coordinate or keyevent 22 + 66)
        # Using ENTER key is often enough if the focus is on the send button
        run_adb("shell input keyevent 22") # Right
        run_adb("shell input keyevent 66") # Enter
        
        return f"📤 WhatsApp mission started on your phone for {number}!"
    except Exception as e:
        return f"❌ WhatsApp via ADB failed: {e}"

def open_app(package_name):
    """Open an app by package name."""
    return run_adb(f"shell monkey -p {package_name} -c android.intent.category.LAUNCHER 1")

def take_screenshot(save_path="data/screen.png"):
    """Take a screenshot of the phone screen."""
    run_adb(f"shell screencap -p /sdcard/screen.png")
    run_adb(f"pull /sdcard/screen.png {save_path}")
    return save_path

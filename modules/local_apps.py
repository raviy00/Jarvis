import os

def launch_app_on_pc(app_name):
    """Launch local windows applications or URL protocol handlers."""
    # Mapping common app names to Windows executables or URI handlers
    apps = {
        "whatsapp": "whatsapp://", 
        "telegram": "tg://", 
        "spotify": "spotify:", 
        "youtube music": "https://music.youtube.com",
        "yt music": "https://music.youtube.com",
        "chrome": "chrome",
        "youtube": "https://youtube.com",
        "notepad": "notepad",
        "calculator": "calc",
        "discord": "discord:",
        "word": "winword",
        "excel": "excel"
    }
    
    # Clean the input slightly ("open whatsapp app" -> "whatsapp")
    app_lower = app_name.lower().replace(" app", "").strip()
    
    # Try mapped dictionary
    if app_lower in apps:
        target = apps[app_lower]
        try:
            os.startfile(target)
            return True, f"Right away, opening {app_name}."
        except Exception as e:
            return False, f"I tried to open {app_name}, but it appears to not be installed or registered."

    # Fallback: Just ask Windows to aggressively start "name"
    try:
        # The empty string "" is for the window title, necessary for start command
        os.system(f'start "" "{app_lower}"')
        return True, f"Attempting to launch {app_name}."
    except Exception:
        return False, f"I couldn't locate {app_name} on your system."

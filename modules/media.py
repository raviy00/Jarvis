# modules/media.py - Media Player Skill for Jarvis
import os
import threading
import pygame
import yt_dlp
from config import ASSISTANT_NAME

# Ensure storage
MEDIA_DIR = "data/media"
if not os.path.exists(MEDIA_DIR):
    os.makedirs(MEDIA_DIR)

# Track current playback
CURRENT_SONG = None

def play_audio(file_path):
    """Play a local audio file (using VLC for best compatibility)."""
    import subprocess
    vlc_path = r"C:\Program Files\VideoLAN\VLC\vlc.exe"
    if os.path.exists(vlc_path):
        try:
            # Run VLC in the background with no interface (dummy)
            subprocess.Popen([vlc_path, "--intf", "dummy", "--play-and-exit", file_path], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"🎵 Jarvis playing (via VLC): {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ VLC playback error: {e}")
    else:
        # Fallback to pygame if VLC is missing
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
            print(f"🎵 Jarvis playing (via Pygame): {os.path.basename(file_path)}")
        except Exception as e:
            print(f"❌ Pygame fallback error: {e}")

def search_and_download(song_query):
    """Search YouTube and download the best audio format."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{MEDIA_DIR}/%(title)s.%(ext)s',
        'quiet': True,
        'noplaylist': True,
        'extract_flat': False,
        # Avoid post-processing since we don't have FFmpeg
    }
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # First search for the video
            info = ydl.extract_info(f"ytsearch1:{song_query}", download=True)
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            
            # Get the path of the downloaded file
            filename = ydl.prepare_filename(video)
            
            # YT-DLP might add an extension or rename, let's check
            # Since we didn't specify a post-processor, it's just the original file
            return filename, video['title']
    except Exception as e:
        print(f"❌ Search/Download error: {e}")
        return None, None

def handle_music_request(query):
    """Entry point for handling 'play song' requests."""
    text_lower = query.lower()
    
    # Handle stop command
    if any(w in text_lower for w in ["stop", "pause", "quiet", "shut up", "end"]):
        return stop_music()

    print(f"🔍 Jarvis searching for music: {query}...")
    
    # Process in background so brain isn't blocked (though brain returns first)
    path, title = search_and_download(query)
    
    if path and os.path.exists(path):
        play_audio(path)
        return f"Sure Ravi, I've found '{title}' from YouTube. Playing it for you now! 🎵"
    else:
        return "I'm sorry Ravi, I couldn't find or download that song right now. Please try again later."

def stop_music():
    """Stop all music playback."""
    # Stop Pygame
    if pygame.mixer.get_init():
        pygame.mixer.music.stop()
        pygame.mixer.music.unload()
    
    # Stop VLC on Windows
    try:
        os.system("taskkill /F /IM vlc.exe /T >nul 2>&1")
    except:
        pass
        
    return "Music stopped."

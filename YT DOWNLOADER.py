from yt_dlp import YoutubeDL
import os
import sys
import re
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
import multiprocessing
from tqdm import tqdm
def sanitize_filename(filename):
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def log_error(message):
    with open("download_errors.log", "a") as log:
        log.write(f"{datetime.now()} - {message}\n")

def get_max_threads():
    return min(3, multiprocessing.cpu_count())
def welcome():
    print(r'''
██╗░░░██╗████████╗  ██████╗░░█████╗░░██╗░░░░░░░██╗███╗░░██╗██╗░░░░░░█████╗░░█████╗░██████╗░███████╗██████╗░
╚██╗░██╔╝╚══██╔══╝  ██╔══██╗██╔══██╗░██║░░██╗░░██║████╗░██║██║░░░░░██╔══██╗██╔══██╗██╔══██╗██╔════╝██╔══██╗
░╚████╔╝░░░░██║░░░  ██║░░██║██║░░██║░╚██╗████╗██╔╝██╔██╗██║██║░░░░░██║░░██║███████║██║░░██║█████╗░░██████╔╝
░░╚██╔╝░░░░░██║░░░  ██║░░██║██║░░██║░░████╔═████║░██║╚████║██║░░░░░██║░░██║██╔══██║██║░░██║██╔══╝░░██╔══██╗
░░░██║░░░░░░██║░░░  ██████╔╝╚█████╔╝░░╚██╔╝░╚██╔╝░██║░╚███║███████╗╚█████╔╝██║░░██║██████╔╝███████╗██║░░██║
░░░╚═╝░░░░░░╚═╝░░░  ╚═════╝░░╚════╝░░░░╚═╝░░░╚═╝░░╚═╝░░╚══╝╚══════╝░╚════╝░╚═╝░░╚═╝╚═════╝░╚══════╝╚═╝░░╚═╝
    ''')
def progress_hook(d):
    if d['status'] == 'downloading':
        print(f"{d['_percent_str']} of {d['filename']}", end='\r')
        sys.stdout.flush()
    elif d['status'] == 'finished':
        print(f"\nFinished: {d['filename']} ✅")
def select_format():
    print("\nSelect video quality:")
    formats = {
        "1": "144",
        "2": "240",
        "3": "360",
        "4": "480",
        "5": "720",
        "6": "1080",
        "7": "best"
    }
    for key, val in formats.items():
        print(f"{key}. {val}p" if val != "best" else f"{key}. Best available")
    
    choice = input("Enter your choice (default 7): ").strip() or "7"
    selected = formats.get(choice, "best")

    if selected == "best":
        return "best"
    else:
        return f"bestvideo[height<={selected}]+bestaudio/best[height<={selected}]"
def download_videos(urls, save_path, format_choice='best'):
    ydl_opts = {
        'format': format_choice,
        'outtmpl': os.path.join(save_path, '%(title)s-%(id)s.%(ext)s'),
        'progress_hooks': [progress_hook],
        'noplaylist': True
    }

    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url.strip() for url in urls if url.strip()])
    except Exception as e:
        print(f"\nError downloading {urls}: {e}")
        log_error(f"URLs: {urls}\nError: {e}")
def download_playlist(url, save_path, format_choice='best'):
    ydl_opts = {
        'format': format_choice,
        'outtmpl': os.path.join(save_path, f"{sanitize_filename('%(playlist_title)s')}/%(title)s-%(id)s.%(ext)s"),
        'progress_hooks': [progress_hook],
        'noplaylist': False
    }
    try:
        with YoutubeDL(ydl_opts) as ydl:
            ydl.download([url.strip()])
    except Exception as e:
        print(f"\nError downloading playlist {url}: {e}")
        log_error(f"Playlist URL: {url}\nError: {e}")
def threaded_download(urls, save_path, format_choice='best', max_threads=3):
    with ThreadPoolExecutor(max_workers=max_threads) as executor:
        futures = [executor.submit(download_videos, [url], save_path, format_choice) for url in urls]
        for future in futures:
            try:
                future.result()
            except Exception as e:
                print(f"Error during download: {e}")
def main():
    welcome()
    default_path = os.path.expanduser("~/yt_videos")
    save_path = input(f"Enter download folder (default: {default_path}): ").strip() or default_path
    os.makedirs(save_path, exist_ok=True)
    max_threads = get_max_threads()
    while True:
        choice = input("\nChoose option:\n1. Single/Multi videos\n2. Playlist\nEnter 1 or 2: ").strip()
        format_choice = select_format()
        if choice == '1':
            urls_input = input("Enter YouTube URLs (comma separated): ").strip()
            urls = [url.strip() for url in urls_input.split(',') if url.strip()]
            if urls:
                threaded_download(urls, save_path, format_choice, max_threads)
            else:
                print("No valid URLs entered.")
        elif choice == '2':
            playlist_url = input("Enter playlist URL: ").strip()
            if playlist_url:
                download_playlist(playlist_url, save_path, format_choice)
            else:
                print("No playlist URL entered.")
        else:
            print("Invalid option. Try again.")

        more = input("\nDo you want to download more? (y/n): ").strip().lower()
        if more != 'y':
            print("Exiting downloader. Goodbye!")
            break

if __name__ == "__main__":
    main()

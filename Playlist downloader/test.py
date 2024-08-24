import os
import csv
import time
import yt_dlp as youtube_dl
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure ffmpeg or avlib is available
ffmpeg_path = r'C:\Users\goldm\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.0.2-essentials_build\bin'
AudioSegment.converter = os.path.join(ffmpeg_path, "ffmpeg")

# Path to your CSV file containing YouTube links
csv_file_path = r'X:\Scripts\Playlist downloader\list.csv'

# Directory to save downloaded videos and converted mp3 files
download_directory = r'E:\PYTUBE'
os.makedirs(download_directory, exist_ok=True)

def get_video_info(link):
    ydl_opts = {
        'format': '251/bestaudio',  # Prefer format 251 (Opus at 136k), fall back to best audio
        'skip_download': True,  # Do not download the file yet, just extract info
        'noplaylist': True,
        'cookies': r'X:\Scripts\Playlist downloader\cookies.txt',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(link, download=False)
            return info_dict
        except youtube_dl.utils.DownloadError as e:
            error_message = str(e)
            if 'Sign in to confirm you’re not a bot' in error_message:
                print(f"Encountered bot protection while fetching info for {link}, pausing for 1 hour...")
                time.sleep(3600)  # Pause for 1 hour
                return get_video_info(link)  # Retry after 1 hour
            else:
                raise

def download_video(link, title):
    ydl_opts = {
        'format': '251/bestaudio',  # Prefer format 251 (Opus at 136k), fall back to best audio
        'outtmpl': os.path.join(download_directory, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_path,
        'noplaylist': True,
        'nocheckcertificate': True,  # Bypass certificate checks (optional)
        'nooverwrites': True,  # Skip already downloaded files
        'cookies': r'X:\Scripts\Playlist downloader\cookies.txt',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(link, download=True)
            return info_dict
        except youtube_dl.utils.DownloadError as e:
            error_message = str(e)
            if 'Sign in to confirm you’re not a bot' in error_message:
                print(f"Encountered bot protection while downloading {link}, pausing for 1 hour...")
                time.sleep(3600)  # Pause for 1 hour
                return download_video(link, title)  # Retry after 1 hour
            else:
                raise

def convert_to_mp3(file_path):
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    mp3_file = os.path.join(download_directory, f"{base_name}.mp3")

    if not os.path.exists(mp3_file):
        audio = AudioSegment.from_file(file_path)
        audio.export(mp3_file, format="mp3", bitrate="320k")
        os.remove(file_path)

    return mp3_file

def check_and_process_link(link):
    try:
        # Get the video info (including title)
        info_dict = get_video_info(link)
        title = info_dict.get('title', 'unknown')
        ext = info_dict.get('ext', 'opus')  # Get the actual file extension
        file_path = os.path.join(download_directory, f"{title}.{ext}")
        mp3_file_path = os.path.join(download_directory, f"{title}.mp3")

        # Check if the file or its MP3 version already exists
        if os.path.exists(file_path) or os.path.exists(mp3_file_path):
            print(f"File '{title}' already exists, skipping download.")
            return None  # Skip further processing

        # If the file doesn't exist, return the link for further processing
        return link
    except Exception as e:
        print(f"Error checking video: {e}")
        return None

def process_link(link):
    if link is None:
        return  # Skip if the file already exists

    try:
        # Get the video info again for processing
        info_dict = get_video_info(link)
        title = info_dict.get('title', 'unknown')
        ext = info_dict.get('ext', 'opus')  # Get the actual file extension

        # Proceed to download and convert
        info_dict = download_video(link, title)
        file_path = os.path.join(download_directory, f"{title}.{ext}")

        if os.path.exists(file_path):
            convert_to_mp3(file_path)

        print(f"Processed: {link}")
    except Exception as e:
        print(f"Error processing video: {e}")

def download_and_convert_all(csv_file):
    links = []

    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            links.append(row[0])

    # Using ThreadPoolExecutor to check files in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(check_and_process_link, link) for link in links]

        # Filter out links that should be processed (those not skipped)
        links_to_process = [future.result() for future in as_completed(futures) if future.result() is not None]

    # Using ThreadPoolExecutor to download and convert in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_link, link) for link in links_to_process]

        for future in as_completed(futures):
            try:
                future.result()
            except Exception as e:
                print(f"Error processing video: {e}")

if __name__ == "__main__":
    download_and_convert_all(csv_file_path)

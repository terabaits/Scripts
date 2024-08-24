import os
import time
import json
import pandas as pd
import yt_dlp
import concurrent.futures

# Paths
urls_path = r'X:\Scripts\Playlist downloader\playlist_urls.csv'
index_file_path = r'X:\Scripts\Playlist downloader\resume_index.json'
downloads_dir = r'E:\PYTUBE'
error_urls_path = r'X:\Scripts\Playlist downloader\error_urls.txt'

# Path to ffmpeg binary directory
ffmpeg_location = r'C:\Users\goldm\AppData\Local\Microsoft\WinGet\Packages\Gyan.FFmpeg.Essentials_Microsoft.Winget.Source_8wekyb3d8bbwe\ffmpeg-7.0.2-essentials_build\bin'

def load_urls(file_path):
    df = pd.read_csv(file_path)
    return df.iloc[:, 0].tolist()  # Assumes URLs are in the first column

def load_last_index(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return 0

def save_last_index(file_path, index):
    with open(file_path, 'w') as f:
        json.dump(index, f)

def append_error_url(file_path, url):
    with open(file_path, 'a') as f:
        f.write(url + '\n')

def download_audio(url, output_dir):
    ydl_opts = {
        'format': 'bestaudio/best',  # Download the best audio format available
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'm4a',  # Save the audio as M4A
            'preferredquality': '192',  # Prefer 192 kbps if possible
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
        'ffmpeg_location': ffmpeg_location,
        'noplaylist': True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except yt_dlp.utils.DownloadError as e:
        if 'Sign in to confirm you’re not a bot' in str(e):
            print(f"Encountered bot check error with {url}. Pausing for 1 hour.")
            time.sleep(3600)  # Pause for 1 hour
            print(f"Resuming download for {url}")
            return download_audio(url, output_dir)  # Retry download after pause
        else:
            print(f"Error downloading {url}: {e}")
            append_error_url(error_urls_path, url)

def download_in_parallel(urls, max_workers=3):
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_url = {executor.submit(download_audio, url, downloads_dir): url for url in urls}
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                future.result()
            except Exception as e:
                print(f"Error occurred with {url}: {e}")
                append_error_url(error_urls_path, url)

input_dir = r'E:\PYTUBE'

# Function to convert M4A to MP3
def convert_to_mp3(input_file, output_file):
    try:
        subprocess.run([
            'ffmpeg',
            '-i', input_file,
            '-codec:a', 'libmp3lame',
            '-b:a', '320k',
            output_file
        ], check=True)
        print(f"Successfully converted {input_file} to {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Error converting {input_file}: {e}")

def convert_all_files(input_dir):
    for filename in os.listdir(input_dir):
        if filename.endswith('.m4a'):
            input_file = os.path.join(input_dir, filename)
            output_file = os.path.join(input_dir, f"{os.path.splitext(filename)[0]}.mp3")
            
            convert_to_mp3(input_file, output_file)

            # Optionally, remove the original M4A file after conversion
            # os.remove(input_file)

if __name__ == '__main__':
    urls = load_urls(urls_path)
    print(f"Loaded {len(urls)} URLs from CSV.")
    last_index = load_last_index(index_file_path)
    
    try:
        urls_to_download = urls[last_index:]
        download_in_parallel(urls_to_download)
    finally:
        save_last_index(index_file_path, len(urls))  # Save the last processed index
    
    convert_all_files(input_dir)
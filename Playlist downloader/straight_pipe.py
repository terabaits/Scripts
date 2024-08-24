import os
import csv
from pytube import YouTube
from pydub import AudioSegment
from concurrent.futures import ThreadPoolExecutor, as_completed

# Ensure ffmpeg or avlib is available
AudioSegment.converter = "ffmpeg"  # or provide the path to ffmpeg executable

# Path to your CSV file containing YouTube links
csv_file_path = r'X:\Scripts\Playlist downloader\list.csv'

# Directory to save downloaded videos and converted mp3 files
download_directory = r'X:\Scripts\Playlist downloader\downloads'
os.makedirs(download_directory, exist_ok=True)

def download_video(link):
    yt = YouTube(link)
    # Get the stream with the best audio quality
    stream = yt.streams.filter(only_audio=True).order_by('abr').desc().first()
    # Download the audio file
    downloaded_file = stream.download(output_path=download_directory)
    return downloaded_file

def convert_to_mp3(file_path):
    # Extract base name without extension
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    mp3_file = os.path.join(download_directory, f"{base_name}.mp3")
    
    # Load the audio file
    audio = AudioSegment.from_file(file_path)
    
    # Export as mp3 with the highest quality
    audio.export(mp3_file, format="mp3", bitrate="320k")
    
    # Optionally remove the original file to save space
    os.remove(file_path)
    
    return mp3_file

def process_link(link):
    downloaded_file = download_video(link)
    mp3_file = convert_to_mp3(downloaded_file)
    return mp3_file

def download_and_convert_all(csv_file):
    links = []
    
    with open(csv_file, 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            links.append(row[0])
    
    # Using ThreadPoolExecutor to download and convert in parallel
    with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_link, link) for link in links]
        
        for future in as_completed(futures):
            try:
                result = future.result()
                print(f"Processed: {result}")
            except Exception as e:
                print(f"Error processing video: {e}")

if __name__ == "__main__":
    download_and_convert_all(csv_file_path)

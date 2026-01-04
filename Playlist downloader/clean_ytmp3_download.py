import os
import time
import json
import pandas as pd
import yt_dlp
import concurrent.futures

def download_audio(video_url, output_folder):
    """Downloads a YouTube video as an MP3 file using yt_dlp."""
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_folder, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
    }],
    'cookiesfrombrowser': ('chrome',)  # Use Chrome's cookies
}

    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(video_url, download=True)
        return info_dict


def process_videos(video_urls, output_folder):
    """Downloads multiple videos as MP3 concurrently."""
    os.makedirs(output_folder, exist_ok=True)
    
cd /home/mks/
git clone https://github.com/mainsail-crew/moonraker-timelapse.git
cd /home/mks/moonraker-timelapse
make install

    metadata = []
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        future_to_url = {executor.submit(download_audio, url, output_folder): url for url in video_urls}
        
        for future in concurrent.futures.as_completed(future_to_url):
            url = future_to_url[future]
            try:
                info = future.result()
                metadata.append({
                    'title': info.get('title', 'Unknown'),
                    'url': url,
                    'filename': info.get('requested_downloads', [{}])[0].get('filepath', 'Unknown')
                })
            except Exception as e:
                print(f"Error downloading {url}: {e}")
    
    # Save metadata to CSV
    df = pd.DataFrame(metadata)
    df.to_csv(os.path.join(output_folder, 'metadata.csv'), index=False)
    print("Download complete. Metadata saved.")

if __name__ == "__main__":
    video_list = [
        'https://www.youtube.com/watch?v=lGRd9QvU-qk'
    ]
    output_directory = "downloads"
    
    start_time = time.time()
    process_videos(video_list, output_directory)
    print(f"Total time taken: {time.time() - start_time:.2f} seconds")
    
yt-dlp -f bestvideo -o '~/Downloads/%(title)s.%(ext)s' "https://www.youtube.com/watch?v=gpRwfegzrXU"

yt-dlp -f bestvideo -o '~/Downloads/%(title)s.%(ext)s' "https://www.youtube.com/watch?v=MkLTKn810T8"

yt-dlp -f bestvideo+bestaudio --merge-output-format mp4 -o '~/Downloads/%(title)s.%(ext)s' "https://www.youtube.com/watch?v=657qx7IkkFk" 

yt-dlp -f bestaudio --extract-audio --audio-format mp3 -o '~/Downloads/%(title)s.%(ext)s' "https://www.youtube.com/watch?v=UaRrDZWhtWA"

''
''
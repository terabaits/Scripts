YouTube Playlist Downloader
This project consists of two main scripts that allow you to download YouTube playlists efficiently.

get_list.py: Extracts a list of video links from a YouTube playlist and saves them in CSV format.
YT_DOWNLOADER_CONVERTER.py: Downloads all the videos from the generated link list, converts them to M4A format, and then automatically converts them to MP3.
Installation & Setup
Follow these steps to install and set up the project:

Install Dependencies: Ensure you have all required dependencies installed. You might need to install packages like yt_dlp, pandas, and watchdog.

Obtain Playlist ID: Get the playlist ID from YouTube. It's the string that follows ?list= in the playlist's URL.

Insert Playlist ID: Open get_list.py and insert your playlist ID where indicated.

Generate URL List: Run get_list.py to create a CSV file containing all the video links from the playlist.

Download and Convert Videos:

Open YT_DOWNLOADER_CONVERTER.py.
Point it to the generated URL CSV file and specify your desired export folder.
Run the script to download and convert the videos.
Features
Parallel Downloads: Downloads up to 3 videos simultaneously for efficient processing.
Bot Protection Handling: Automatically pauses after 730 downloads to avoid bot detection, resuming after a 1-hour delay.
Auto-Resume: The last processed row index in the CSV is saved, allowing the download to resume from where it left off in case of failure.
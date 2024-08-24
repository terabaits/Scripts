import csv
from pytube import Playlist

# Function to get all video links from a YouTube playlist and save to CSV
def save_playlist_links_to_csv(playlist_url, csv_filename):
    # Create a Playlist object
    playlist = Playlist(playlist_url)

    # Open a CSV file to write
    with open(csv_filename, 'w', newline='') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Video Title', 'URL'])  # Write the header row

        # Iterate through all the video URLs in the playlist
        for video in playlist.videos:
            video_url = video.watch_url
            video_title = video.title
            writer.writerow([video_title, video_url])  # Write title and URL to the CSV

    print(f'Successfully saved {len(playlist.video_urls)} videos to {csv_filename}')

# Example usage
playlist_url = 'https://www.youtube.com/playlist?list=FLY2hdiNTV-d04JjPg1IV9Ng'  # Replace with your playlist URL
csv_filename = 'playlist_links.csv'  # Specify the desired CSV filename

save_playlist_links_to_csv(playlist_url, csv_filename)

import yt_dlp
import os


def download_video_simple(url, output_path='.', proxy=None):
    ydl_opts = {
        'merge_output_format': 'mp4',
        'format': 'bestvideo+bestaudio/best',
        'outtmpl': f'{output_path}/%(title)s.%(ext)s',
    }
    if proxy:
        ydl_opts['proxy'] = proxy
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

def download_video(url, archive_file='~/Downloads/downloaded_archive.txt', proxy=None):
    if not os.path.exists(archive_file):
        open(archive_file, 'a').close()
    ydl_opts = {
        'format': 'best',
        'outtmpl': '~/Downloads/%(title)s.%(ext)s',
        'download_archive': archive_file, # Specify the archive file
        'ignoreerrors': True, # Continue if some videos fail
        'verbose': False # Set to True for more detailed output
    }
    if proxy:
        ydl_opts['proxy'] = proxy
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False) # Extract info without downloading
            video_id = info_dict.get('id')

            # Check if the video ID is in the archive file
            with open(archive_file, 'r') as f:
                if video_id in f.read():
                    print(f"Video '{info_dict.get('title')}' (ID: {video_id}) already downloaded. Skipping.")
                    return True
                else:
                    print(f"Downloading video '{info_dict.get('title')}' (ID: {video_id})...")
                    ydl.download([url]) # Download if not in archive
        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    print("Download check and process complete.")

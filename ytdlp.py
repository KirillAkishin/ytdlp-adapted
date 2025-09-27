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

def download_video(url, output_path='.', preset='best', proxy=None):
    download_archive = os.path.join(output_path, "downloaded_archive.txt") 
    outtmpl = os.path.join(output_path, "%(title)s.%(ext)s")    
    opts_dict = {
        'best': {
            'merge_output_format': 'mp4',
            'format': 'bestvideo+bestaudio/best',
            'outtmpl': outtmpl,
        },
        'test': {
            'format': 'best',
            'outtmpl': outtmpl,
            'download_archive': download_archive, # Exclude the listed files from downloading
            'ignoreerrors': True, # Continue if some videos fail
            'verbose': False 
        }
    }
    if not os.path.exists(download_archive):
        open(download_archive, 'a').close()
    ydl_opts = opts_dict[preset]
    if proxy:
        ydl_opts['proxy'] = proxy
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info_dict = ydl.extract_info(url, download=False) # Extract info without downloading
            video_id = info_dict.get('id')

            # Check if the video ID is in the archive file
            with open(download_archive, 'r') as f:
                if video_id in f.read():
                    print(f"Video '{info_dict.get('title')}' (ID: {video_id}) already downloaded. Skipping.")
                    return True
                else:
                    print(f"Downloading video '{info_dict.get('title')}' (ID: {video_id})...")
                    ydl.download([url]) # Download if not in archive
        except Exception as e:
            print(f"Error processing URL {url}: {e}")

    print("Download check and process complete.")

import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import requests
from tqdm import tqdm
import os
from pathlib import Path
import datetime
import random
import time
import yt_dlp


def get_request(url="https://example.com", timeout=5, http_proxy_address=None, **kwargs):
    if http_proxy_address:
            proxies = {
                "http": f"http://{http_proxy_address}",
                "https": f"http://{http_proxy_address}",
            }
            # proxies = {
            #     "http": http_proxy_address,
            #     "https": http_proxy_address,
            # }
            kwargs = {**kwargs, **{"proxies": proxies,}}
    try:
        response = requests.get(url, timeout=timeout, **kwargs)
        if response.status_code == 200:
            logging.debug(f"Good request: {response.status_code}")
            return response
        else:
            logging.debug(f"Bad request: {response.status_code}")
            return response
    except requests.exceptions.RequestException as e:
        logging.debug(f"Failed request: {e}")
        return None

def check_http_proxy(test_url, http_proxy_address):
    resp = get_request(test_url, http_proxy_address=http_proxy_address)
    if resp and resp.status_code == 200:
        resp_ip = resp.text[:15].strip()
        if resp.headers.get('content-type') == 'application/json':
            resp_ip = resp.json().get('origin')
        logging.debug(f"Proxy {http_proxy_address} is working. IP: {resp_ip}")
        return True
    logging.debug(f"Proxy {http_proxy_address} failed.")
    return False

def proxy_provider_request(get_proxies_url, test_urls=None):
    resp_provider = get_request(get_proxies_url, timeout=30)
    if resp_provider and resp_provider.status_code == 200:
        proxy_list = resp_provider.text.split()
        good_proxy_list = proxy_list
        if test_urls:
            good_proxy_list = list()
            for proxy in tqdm(proxy_list):
                for url in test_urls:
                    if check_http_proxy(url, proxy):
                        good_proxy_list.append(proxy)
                        break
            logging.debug(f"All {len(proxy_list)} proxies are checked.")
        if len(good_proxy_list) != 0:
            logging.info(f"{len(good_proxy_list)} working proxies found.")
            return set(good_proxy_list)
    return set()

def get_proxy_pool(request_pool, test_urls=None):
    if test_urls is None:
        test_urls = [
            # "http://2ip.io",
            "http://ifconfig.me",
            "http://icanhazip.com",
            "http://httpbin.org/ip",
            "http://ipecho.net/plain",
        ]
    proxy_pool = dict()
    for protocol, request_list in request_pool.items():
        logging.info(f"{protocol.upper()} protocol processing.")
        proxy_pool[protocol] = set()
        for req in request_list:
            proxy_pool[protocol].update(proxy_provider_request(req, test_urls=test_urls))
    logging.warning(f"{sum([len(v) for v in proxy_pool.values()])} working proxies found (total).")
    return proxy_pool

def resolve_path(path_str: str) -> Path:
    expanded_vars = os.path.expandvars(path_str)
    expanded_user = Path(expanded_vars).expanduser()
    absolute_path = expanded_user.resolve()
    return absolute_path

def get_proxies(proxy_file="~/.proxies_test.txt"):
    request_pool = {
        "https": [
            "https://api.best-proxies.ru/proxylist.txt?key=developer&type=https&limit=10",
        ],
        "http": [
            "https://api.best-proxies.ru/proxylist.txt?key=developer&type=http&limit=10",
        ],
        # "socks5": [
            # "https://api.best-proxies.ru/proxylist.txt?key=developer&type=socks5&limit=10",
        # ],
        # "socks4": [
            # "https://api.best-proxies.ru/proxylist.txt?key=developer&type=socks4&limit=10",
        # ],
    }
    proxy_pool = get_proxy_pool(request_pool)
    with open(resolve_path(proxy_file), "w") as f:
        for protocol, proxies_set in proxy_pool.items():
            for proxy in proxies_set:
                f.write(f"{protocol}://{proxy}\n")


def when_modified(file_path: str) -> datetime.datetime | None:
    if not os.path.exists(file_path):
        logging.debug(f"Error! The file '{file_path}' not found.")
        return None
    mod_timestamp = os.path.getmtime(file_path)
    mod_datetime = datetime.datetime.fromtimestamp(mod_timestamp)
    logging.debug(f"The file '{file_path}' was last modified on: {mod_datetime}")
    return mod_datetime

def duration_calculator(dt_end:datetime.datetime = None, dt_srt:datetime.datetime = None) -> datetime.timedelta:
    dt_now = datetime.datetime.now()
    dt_end = dt_end if dt_end else dt_now
    dt_srt = dt_srt if dt_srt else dt_now
    return dt_end - dt_srt

def get_one_proxy(proxy_file:str="~/.proxies_test.txt", expiration:int=10, force_reload:bool=False):
    file_path = resolve_path(proxy_file)
    dt_mod = when_modified(file_path)
    dt_mod_passed = duration_calculator(dt_mod)
    if force_reload or abs(dt_mod_passed.total_seconds()) > expiration*60:
        logging.info("Loading new proxy pool.")
        get_proxies()
    with open(file_path, "r") as f:
        proxy_pool = []
        for line in f:
            proxy_pool.append(line.strip())
    return random.choice(proxy_pool)

def proxy_generator(proxy_file:str="~/.proxies_test.txt", expiration:int=10, repetitions: int | bool = True):
    file_path = resolve_path(proxy_file)

    def gen():
        dt_mod = when_modified(file_path)
        dt_mod_passed = duration_calculator(dt_mod)
        if abs(dt_mod_passed.total_seconds()) > expiration*60:
            logging.info("Proxy pool mining.")
            get_proxies()
        with open(file_path, "r") as f:
            for line in f:
                yield line.strip()

    attempt = 0
    repetitions = repetitions if repetitions else 1
    while repetitions:
        for p in gen():
            attempt += 1
            logging.debug(f"{attempt} try")
            yield p
        if repetitions is not True:
            repetitions -= 1
        time.sleep(10)


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


### MAIN ###
if __name__ == '__main__':
    logging.critical('restart')
    url_video = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
    # url_example = 'https://example.com'
    url_example = "http://ifconfig.me"
    output_path = '~/Downloads/test_dir'

    for proxy in proxy_generator(expiration=15):
        print(f"try proxy: {proxy}", end='\t')
        download_video_simple(url_video, output_path=output_path, proxy=proxy.split("://")[1])
        # resp = get_request(url=url_example, http_proxy_address=proxy.split("://")[1])
        time.sleep(0.1)

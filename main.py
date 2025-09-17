import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

import time
from ytdlp import download_video, download_video_simple
from proxy import *

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

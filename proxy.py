import logging
from tqdm import tqdm
import random
import requests
import time
from common import when_modified, duration_calculator, resolve_path

def get_request(url="https://example.com", timeout=5, http_proxy=None, **kwargs):
    if http_proxy:
            proxies = {
                "http": http_proxy,
                "https": http_proxy,
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

def check_http_proxy(test_url, http_proxy):
    resp = get_request(test_url, http_proxy=http_proxy)
    if resp and resp.status_code == 200:
        resp_ip = resp.text[:15].strip()
        if resp.headers.get('content-type') == 'application/json':
            resp_ip = resp.json().get('origin')
        logging.debug(f"Proxy {http_proxy} is working. IP: {resp_ip}")
        return True
    logging.debug(f"Proxy {http_proxy} failed.")
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


# todo: ProxyAdapter
class ProxyAdapter:
    def __init__(self, proxy_pool=dict()):
        # сохранение пула прокси на диск/в оперативку
        self.proxy_pool = proxy_pool

    def get_request_force(self, **kwargs):
        resp = self.get_request(**kwargs)
        if resp and resp.status_code == 200:
            return resp
        # если у запроса указано конкретное прокси через которое надо соединяться,
        # то просто продолжать выполнение функции — плохое поведение
        if kwargs['http_proxy']:
            return None
        # todo: socks4/5
        for protocol, proxy_set in self.proxy_pool.values():
            for proxy in proxy_set:
                pass
                resp = self.get_request(**kwargs)
                if resp and resp.status_code == 200:
                    return resp
                pass

    def _get_request():
        pass
    def _get_request_via_proxy():
        pass

    def get_request(self, url="https://example.com", timeout=5, http_proxy=None, **kwargs):
        if http_proxy:
            proxies = {
                "http": f"http://{http_proxy}",
                "https": f"http://{http_proxy}",
            }
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


import requests, logging
from tqdm import tqdm

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

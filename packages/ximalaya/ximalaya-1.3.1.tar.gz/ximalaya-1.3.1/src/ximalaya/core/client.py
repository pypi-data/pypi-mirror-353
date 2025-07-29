import logging
from typing import Generic, Iterator, Type, TypeVar

import requests
from jsonpath_ng import parse


class XimalayaClient:
    host: str

    def __init__(self, host: str = 'www.ximalaya.com', *, headers: dict = None):
        self.host = host

        self.headers = {} if headers is None else headers

        if 'User-Agent' not in self.headers:
            self.headers['User-Agent'] = ''

    def get(self, path: str, *, params: dict = None) -> dict:
        url = f'https://{self.host}/{path.lstrip("/")}'

        if params is None:
            params = {}

        logging.debug('[XimalayaClient][GET]: %s', url)

        r = requests.get(url=url, headers=self.headers, params=params)

        if r.status_code != 200:
            raise requests.HTTPError(r.content.decode('utf-8'))

        return r.json()


T = TypeVar('T')


class ResponsePaginator(Generic[T], Iterator):
    client: XimalayaClient
    url: str
    item_class: Type[T]
    params: dict
    page_key: str
    page_num: int

    def __init__(self,
                 client: XimalayaClient,
                 *,
                 url: str,
                 params: dict = None,
                 data_path: str,
                 item_class: Type[T],
                 page_key: str = 'page',
                 page_num: int = 1):
        self.client = client
        self.url = url
        self.params = {} if params is None else params
        self.item_class = item_class
        self.page_key = page_key
        self.page_num = page_num
        self.jsonpath_expression = parse(f'$.{data_path}')

    def __next__(self) -> list[T]:
        json_data = self.client.get(self.url, params={self.page_key: self.page_num, **self.params})

        match = self.jsonpath_expression.find(json_data)

        if match is None or len(match[0].value) == 0:
            raise StopIteration()

        self.page_num += 1

        return [self.item_class(**item) for item in match[0].value]

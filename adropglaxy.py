import re
import asyncio
import sys
from typing import AsyncGenerator, List
from bs4 import BeautifulSoup
import httpx


class DropGalaxy:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.base_url = "https://dropgalaxy.co/"
        self.client = client

    async def _get_token(self, id: str) -> str:
        token = f"[hostname=dropgalaxy.co][id={id}]"
        msg = [ord(x) for x in token]
        msg = str(msg).replace('[', '').replace(']', '')
        msg = msg.replace('2', '004').replace('3', '005').replace('7', '007')
        msg = re.sub(r',0,0,0', '', msg)
        headers = {
            'authority': 'tmp.isavetube.com',
            'accept': '*/*',
            'accept-language': 'en-US,en;q=0.8',
            'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'origin': 'https://dropgalaxy.co',
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
        data = {
                'rand': '',
                'msg': msg
                }

        resp = await self.client.post('https://tmp.isavetube.com/gettoken.php',
                                      data=data,
                                      headers=headers)
        return resp.text

    async def _get_link(self, id: str) -> str:
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
        data = {
            'op': 'download2',
            'id': id,
            'xd': await self._get_token(id)
        }

        resp = await self.client.post(self.base_url + id,
                                      headers=headers,
                                      data=data)
        soup = BeautifulSoup(resp.content, 'html.parser')
        form_element = soup.find('form', id='dllink')
        if form_element:
            zip_url = form_element.get('action')  # type: ignore
            return zip_url  # type: ignore

        else:
            raise ValueError()

    def _link_id(self, url: str) -> str:
        return url.split('/')[-1]

    async def __call__(self, url_array: List[str]) -> List[str]:
        ids = (self._link_id(url) for url in url_array)
        tasks = (self._get_link(id) for id in ids)
        urls = await asyncio.gather(*tasks)
        return urls


async def main() -> None:
    try:
        urls = sys.argv[1:]
    except IndexError:
        print(f"{sys.argv[0]} [link]")
        exit()
    async with httpx.AsyncClient() as client:
        resolver = DropGalaxy(client)
        links = await resolver(urls)
        for link in links:
            print(link)


if __name__ == '__main__':
    asyncio.run(main())

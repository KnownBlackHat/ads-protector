import asyncio
import logging
from selectolax.parser import HTMLParser
import re
import sys
from typing import Set

import httpx

logger = logging.getLogger(__name__)
logging.basicConfig(
    format="%(levelname)s: %(message)s",
    level=logging.INFO,
    handlers=[logging.NullHandler()],
)
logger = logging.getLogger(__name__)


class DropGalaxy:
    def __init__(self, client: httpx.AsyncClient) -> None:
        self.base_url = "https://dropgalaxy.co/drive/"
        self.client = client

    async def _get_token(self, id: str) -> str:
        token = f"[LODA-LELO][hostname=dropgalaxy.com][id={id}][adb=0][frminfo=][offset=300][scr=https://script.4dex.io/localstore.js]"
        msg = [ord(x) for x in token]
        msg = str(msg).replace("[", "").replace("]", "")
        msg = msg.replace("2", "004").replace("3", "005").replace("7", "007")
        msg = re.sub(r",0,0,0", "", msg)
        headers = {
            "authority": "tmp.isavetube.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://dropgalaxy.co",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }
        data = {"rand": "", "msg": msg}

        resp = await self.client.post(
            "https://tmp.isavetube.com/gettoken.php?u=div-gpt-ad-dropgalaxycom&v=script2.src", data=data, headers=headers
        )
        return resp.text

    async def _get_link(self, id: str) -> str | None:
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"
        }
        data = {"op": "download2", "id": id, "xd": await self._get_token(id)}

        resp = await self.client.post(self.base_url + id, headers=headers, data=data)
        html = HTMLParser(resp.content)
        try:
            zip_url = html.css_first('#dllink').attributes.get('action')
        except AttributeError:
            logger.critical(f"Unable to get zip url {data=!r}")
            print(f"{data=!r}")
            return None
        else:
            return zip_url

    def _link_id(self, url: str) -> str:
        return url.split("/")[-1]

    async def __call__(self, url_array: Set[str]) -> Set[str]:
        ids = {self._link_id(url) for url in url_array}
        tasks = {self._get_link(id) for id in ids}
        urls = await asyncio.gather(*tasks)
        return set(urls)


async def main() -> None:
    try:
        urls = sys.argv[1:]
    except IndexError:
        print(f"{sys.argv[0]} [link]")
        exit()
    async with httpx.AsyncClient() as client:
        resolver = DropGalaxy(client)
        links = await resolver(set(urls))
        for link in links:
            print(link)


if __name__ == "__main__":
    asyncio.run(main())

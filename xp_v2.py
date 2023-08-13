import sys
import asyncio
from bs4 import BeautifulSoup
from requests.models import InvalidURL
import httpx


class XpLinks:
    def __init__(self, url, client: httpx.AsyncClient) -> None:
        self.id = url.split('/')[-1]
        self.base_url = url[:-len(self.id)]
        self.url = url
        self.client = client

    async def _get_referer(self) -> str:
        resp = await self.client.get(self.url)
        return resp.headers.get('location').split('/')[2]

    async def _get_data(self) -> dict:
        """Gets the data needed to get the link"""

        HEADERS = {
                "User-Agent": "Magic Browser",
                "Referer": f'https://{await self._get_referer()}/'
                }
        response = await self.client.get(self.base_url + self.id,
                                         headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")
        cookie = dict()
        for key, val in response.cookies.items():
            cookie[key] = val
        try:
            return {
                    "ad_form_data":
                    soup.find("input", {"name": "ad_form_data"})["value"],  # type: ignore
                    "token_field":
                    soup.find("input", {"name": "_Token[fields]"})["value"],  # type: ignore
                    "token_unlocked":
                    soup.find("input", {"name": "_Token[unlocked]"})["value"],  # type: ignore
                    "csrf_token": str(response.cookies.get("csrfToken")),
                    "cookie": response.cookies
                    }
        except TypeError:
            raise InvalidURL

    async def _get_link(self, data: dict) -> str:
        """Gets the link"""

        ad_form_data = data["ad_form_data"]
        token_field = data["token_field"]
        token_unlocked = data["token_unlocked"]
        csrf_token = data["csrf_token"]
        cookie = data["cookie"]

        HEADERS = {
                'user-agent': 'Magic Browser',
                'accept': 'application/json, text/javascript, */*; q=0.01',
                'accept-language': 'en-US,en;q=0.5',
                'content-type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'x-requested-with': 'XMLHttpRequest'
                }

        data = {
              "_method": "POST",
              "_csrfToken": csrf_token,
              "ad_form_data": ad_form_data,
              "_Token[fields]": token_field,
              "_Token[unlocked]": token_unlocked
              }
        response = await self.client.post(self.base_url + "links/go",
                                          headers=HEADERS,
                                          cookies=cookie,
                                          data=data)

        try:
            return response.json()["url"]
        except IndexError:
            raise Exception("Unable to get link")

    async def link(self) -> str:
        data = await self._get_data()
        await asyncio.sleep(10)
        link = await self._get_link(data)
        return link


async def main():
    try:
        sys.argv[1]
    except IndexError:
        print(f"Usage: {sys.argv[0]} [links | id]")
        exit()
    try:
        links = sys.argv[1:]

        async def _worker(url, client):
            bypass = XpLinks(url, client)
            print(bypass.id)
            return await bypass.link()
        async with httpx.AsyncClient(timeout=httpx.Timeout(None)) as client:
            tasks = [_worker(x, client) for x in links]
            links = await asyncio.gather(*tasks)
        print(links)

    except (KeyboardInterrupt, EOFError, SystemExit):
        print("Exitting... ")
        exit()


if __name__ == "__main__":
    asyncio.run(main())

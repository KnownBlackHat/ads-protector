import sys
from typing import List, Generator
import requests
from time import sleep
from bs4 import BeautifulSoup
from requests.models import HTTPError, InvalidURL


class XpLink:
    def __init__(self) -> None:
        self.referer = None
        self.base_url = "https://xpshort.com/"

    def _get_referer(self) -> str:
        """Returns location header value"""

        resp = requests.get(self.base_url + "1", allow_redirects=False)
        return f"https://{str(resp.headers.get('location')).split('/')[2]}/"

    def _get_data(self, search_id: str) -> dict:
        """Gets the data needed to get the link"""

        if search_id.startswith('http'):
            search_id = search_id.split('/')[-1]
        if not self.referer:
            self.referer = self._get_referer()
        HEADERS = {
                "User-Agent": "Magic Browser",
                "Referer": self.referer
                }
        response = requests.get(self.base_url + search_id, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")

        try:
            response.raise_for_status()
            return {
                    "ad_form_data":
                    soup.find("input", {"name": "ad_form_data"})["value"],  # type: ignore
                    "token_field":
                    soup.find("input", {"name": "_Token[fields]"})["value"],  # type: ignore
                    "token_unlocked":
                    soup.find("input", {"name": "_Token[unlocked]"})["value"],  # type: ignore
                    "csrf_token": response.cookies.get("csrfToken"),
                    "cookie": response.cookies
                    }
        except (TypeError, HTTPError) as e:
            raise InvalidURL(e)

    def _get_link(self, data: dict) -> str:
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
        response = requests.post(self.base_url + "links/go",
                                 headers=HEADERS,
                                 cookies=cookie,
                                 data={
                                     "_method": "POST",
                                     "_csrfToken": csrf_token,
                                     "ad_form_data": ad_form_data,
                                     "_Token[fields]": token_field,
                                     "_Token[unlocked]": token_unlocked
                                     })
        json_dat = response.json()
        try:
            response.raise_for_status()
            if json_dat.get("status") == "success":
                return response.json()["url"]
            else:
                raise HTTPError(json_dat)
        except HTTPError:
            raise HTTPError(json_dat)

    def resolve_links(self, links: List[str]) -> Generator:
        resolved_id = [id for id in map(lambda x: self._get_data(x), links)]
        sleep(6)
        resolved_links = (link for link in map(lambda x: self._get_link(x),
                                               resolved_id))
        return resolved_links


def main():
    try:
        sys.argv[1]
    except IndexError:
        print(f"Usage: {sys.argv[0]} [links | id]")
        exit()
    try:
        links = sys.argv[1:]
        resolver = XpLink()
        gen = resolver.resolve_links(links)
        for i in gen:
            print(i)
    except (KeyboardInterrupt, EOFError, SystemExit):
        print("Exitting... ")
        exit()


if __name__ == "__main__":
    main()

import sys
import requests
from time import sleep
from bs4 import BeautifulSoup


BASE_URL = "https://xpshort.com/"
REFERER = "https://www.apanmusic.in/"


def get_data(search_id: str) -> dict:
    """Gets the data needed to get the link"""

    if search_id.startswith('http'):
        search_id = search_id.split('/')[-1]
    HEADERS = {
            "User-Agent": "Magic Browser",
            "Referer": REFERER
            }
    response1 = requests.get(BASE_URL + search_id, headers=HEADERS)
    soup = BeautifulSoup(response1.content, "html.parser")

    try:
        return {
                "ad_form_data":
                soup.find("input", {"name": "ad_form_data"})["value"],  # type: ignore
                "token_field":
                soup.find("input", {"name": "_Token[fields]"})["value"],  # type: ignore
                "token_unlocked":
                soup.find("input", {"name": "_Token[unlocked]"})["value"],  # type: ignore
                "csrf_token": response1.cookies["csrfToken"],
                "cookie": response1.cookies.get_dict()
                }
    except TypeError:
        raise Exception("Invalid search id")


def get_link(data: dict) -> str:
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
    response2 = requests.post(BASE_URL + "links/go",
                              headers=HEADERS,
                              cookies=cookie,
                              data={
                                  "_method": "POST",
                                  "_csrfToken": csrf_token,
                                  "ad_form_data": ad_form_data,
                                  "_Token[fields]": token_field,
                                  "_Token[unlocked]": token_unlocked
                                  })

    if response2 and response2.json()["status"] == "success":
        return response2.json()["url"]
    else:
        print(response2.json())
        raise Exception("Unable to get link")


def main():
    try:
        sys.argv[1]
    except IndexError:
        print(f"Usage: {sys.argv[0]} [links | id]")
        exit()
    try:
        links = sys.argv[1:]
        resolved_id = [ id for id in map(lambda x: get_data(x), links) ]
        sleep(6)
        resolved_links = [ link for link in map(lambda x: get_link(x), resolved_id) ]
        for i in resolved_links:
            print(i)
    except (KeyboardInterrupt, EOFError, SystemExit):
        print("Exitting... ")
        exit()


if __name__ == "__main__":
    main()

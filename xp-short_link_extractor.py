import requests
import time
from bs4 import BeautifulSoup


BASE_URL = "https://xpshort.com/"
REFERER = "https://a.finsurances.co/"


def get_data(search_id: str) -> dict:
    """Gets the data needed to get the link"""

    HEADERS = {
            "User-Agent": "Magic Browser",
            "Referer": REFERER
            }
    response1 = requests.get(BASE_URL + search_id, headers=HEADERS)
    soup = BeautifulSoup(response1.content, "html.parser")

    try:
        return {
                "ad_form_data":
                soup.find("input", {"name": "ad_form_data"})["value"],
                "token_field":
                soup.find("input", {"name": "_Token[fields]"})["value"],
                "token_unlocked":
                soup.find("input", {"name": "_Token[unlocked]"})["value"],
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


while True:
    try:
        search_id = " ".join(input("\n [+] Enter the search id: ").split())

        if search_id == "exit" or search_id == "quit":
            raise KeyboardInterrupt
        elif "/" in search_id:
            print("\n [!] '/' Character not allowed")
            continue
        else:
            print("\n [*] Searching for id...")
            search_data = []
            error_bool = False
            for id in search_id.split(" "):
                try:
                    search_data.append(get_data(id))
                except Exception as e:
                    print("\n [!] Error: " + str(e))
                    error_bool = True
                    break

            if error_bool:
                continue
            time.sleep(6)

            print("\n [*] Searching for Link...")
            for data in search_data:
                try:
                    print("\n [+] Link: " + get_link(data))
                except Exception as e:
                    print("\n [!] Error: " + str(e))
                    break

    except (KeyboardInterrupt, EOFError, SystemExit):
        print("\n\n [!] Exiting...")
        break

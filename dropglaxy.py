import re
import sys
from bs4 import BeautifulSoup
import requests as req


class DropGalaxy:
    def __init__(self, url: str) -> None:
        self.url = url
        self.id = url.split('/')[-1]

    def get_token(self) -> str:
        token = f"[hostname=dropgalaxy.co][id={self.id}]"
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

        resp = req.post('https://tmp.isavetube.com/gettoken.php',
                        data=data,
                        headers=headers)
        return resp.text

    def get_link(self) -> str:
        headers = {
            'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36'
        }
        xd = self.get_token()
        data = {
            'op': 'download2',
            'id': self.id,
            'xd': xd,
        }

        resp = req.post(self.url, headers=headers, data=data)
        soup = BeautifulSoup(resp.content, 'html.parser')
        form_element = soup.find('form', id='dllink')
        if form_element:
            zip_url = form_element.get('action')  # type: ignore
            return zip_url  # type: ignore

        else:
            raise ValueError()


if __name__ == '__main__':
    try:
        urls = sys.argv[1:]
    except IndexError:
        print(f"{sys.argv[0]} [link]")
        exit()
    for url in urls:
        drpglxy = DropGalaxy(url)
        print(drpglxy.get_link())

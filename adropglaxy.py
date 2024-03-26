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
        token = '[download adguard unlocked version][LODA-LELO][hostname=financemonk.net][x=][referer=undefined][rand=][id=][adb=1][dropgalaxyisbest=0][adblock_detected=1][downloadhash=][downloadhashad=1][tmz=Eastern Daylight Time][hgt=1115][usrtm=19.388][offset=240][agent=Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0][fthd=1][chngd=74][finum=4][finun=3][fivis=1][fihei=2][ndgmf=block][frminfo=[{"id":"iframe","width":320,"height":50,"src":"https://ad.a-ads.com/1638143?size=320x50","allowFullscreen":false},{"id":"iframe","width":0,"height":0,"src":"https://ee1e90b8db6ded7e2085e076beaa75bc.safeframe.googlesyndication.com/safeframe/1-0-40/html/container.html","allowFullscreen":false},{"id":"iframe","width":0,"height":0,"src":"https://tpc.googlesyndication.com/sodar/sodar2/225/runner.html","allowFullscreen":false},{"id":"iframe","width":0,"height":0,"src":"https://www.google.com/recaptcha/api2/aframe","allowFullscreen":false}]][ddd=[{"id":"div-gpt-ad-1694620036280-0","style":"display: none; min-width: 728px; min-height: 90px;"},{"id":"google_ads_iframe_/22658273219/desktop1_0__container__","style":"border: 0pt none; width: 728px; height: 0px;"},{"id":"div-gpt-ad-1694620133411-0","style":"min-width: 200px; min-height: 100px; display: none;"},{"id":"google_ads_iframe_/22658273219/mobile3_0__container__","style":"border: 0pt none; width: 250px; height: 0px;"},{"id":"dgpromo","style":"display: block;"},{"id":"div-gpt-ad-1694618678860-0","style":"min-width: 200px; min-height: 200px; display: none;"},{"id":"downloadbtn","style":"display: none;"},{"id":"downloadBtnClick","style":"display: block;"},{"id":"div-gpt-ad-1694618958058-0","style":"min-width: 200px; min-height: 200px; display: none;"},{"id":"google_ads_iframe_/22658273219/mobile2_0__container__","style":"border: 0pt none; width: 200px; height: 0px;"},{"id":"desktopagent","style":"display: none;"},{"id":"firefoxagent","style":"display: block;"},{"id":"error_id","style":"color:green;"},{"id":"txtareabk","style":"display:none;"},{"id":"analytics","style":"display: none;"},{"id":"tokens","style":"display:none;"},{"id":"pppppppp","style":"display:none;"},{"id":"div-gpt-ad-1694619903954-0","style":"min-width: 120px; min-height: 60px;"},{"id":"div-gpt-ad-1694619797059-0","style":"min-width: 300px; min-height: 50px;"},{"id":"coloriddiv","style":"display: none;"}]][actv=true][ncripts=33][ntyle=3][nvids=46][vidn=10][setoff=240][divs=46][divsnone=10][offset=240][scr=https://securepubads.g.doubleclick.net/pagead/managed/js/gpt/m202403190101/pubads_impl_page_level_ads.js][scr=https://cdnjs.cloudflare.com/ajax/libs/jquery/1.9.1/jquery.min.js][scr=/adgpt.js][scr=https://assets-7pb.pages.dev/js/jquery.paging.js][scr=https://assets-7pb.pages.dev/js/jquery.cookie.js][scr=https://assets-7pb.pages.dev/js/paging.js?v=1130][scr=https://securepubads.g.doubleclick.net/tag/js/gpt.js][scr=https://securepubads.g.doubleclick.net/pagead/managed/js/gpt/m202403190101/pubads_impl.js][ifc=2][vli=0][stl=1][ps=0]'
        token = token.replace('[id=]', f'[id={id}]')
        token = token.replace('[x=]', '')
        msg = [ord(x) for x in token]
        msg = str(msg).replace("[", "").replace("]", "")
        msg = msg.replace("2", "004").replace("3", "005").replace("7", "007")
        msg = re.sub(r",0,0,0", "", msg)
        headers = {
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.8",
            "content-type": "application/x-www-form-urlencoded; charset=UTF-8",
            "origin": "https://financemonk.net",
            "referer": "https://financemonk.net/",
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
        }
        data = {"rand": "", "msg": msg}

        resp = await self.client.post(
            "https://tmp.isavetube.com/gettoken.php?u=div-gpt-ad-dropgalaxycom&v=popunder&usr=hidden", data=data, headers=headers
        )
        return resp.text

    async def _get_link(self, id: str) -> str | None:
        headers = {
            "user-agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0"
        }
        data = {"op": "download2", "id": id, "xd": await self._get_token(id)}

        resp = await self.client.post(self.base_url + id, headers=headers, data=data)
        html = HTMLParser(resp.content)
        try:
            zip_url = html.css_first('input[name=downloadlink]').attributes.get('value')
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

import asyncio
from functools import reduce

import aiohttp
from bs4 import BeautifulSoup

from classes import EducationalProgram, AbiturSimplified, MIPTCompetitiveDev
from config import HEADERS, SAVE_PATH
from utlis import save_to_csv


async def parse_competitive_url_table_row(tr: BeautifulSoup) -> tuple[str, list[str | None]] | str:
    """Parses row from competitive groups table.

    :param tr: found <tr> tag.
    :returns: list of urls to educational program (if type of competitive group
    doesn't exist, returns None at the appropriate position) or name of educational
    program.
    """
    tds = tr.find_all("td")
    if len(tds) == 2:
        name, _ = tds
        return name.text
    elif len(tds) == 6:
        sub_name, *cgs = tds
    else:
        _, sub_name, *cgs = tds

    sub_name = sub_name.text
    cg_urls = []
    for cg in cgs:
        a_tag = cg.find("a")
        if a_tag is not None:
            cg_urls.append(a_tag.get("href"))
        else:
            cg_urls.append(None)

    return sub_name, cg_urls


async def raw_data_to_dc_list(raw: list[tuple[str, list[str | None]] | str]) -> list[MIPTCompetitiveDev]:
    """

    :param raw:
    :return:
    """
    assert isinstance(raw[0], str), "List must starts with educational program name!"
    competitive = {0: "budget", 1: "quote1", 2: "quote2", 3: "quote3", 4: "contract"}
    ret = []
    for item in raw:
        if isinstance(item, str):
            name = item
        else:
            sub_name, urls = item
            for i, url in enumerate(urls):
                if url is not None:
                    ret.append(MIPTCompetitiveDev(name=name, sub_name=sub_name, competitive=competitive[i], url=url))

    return ret


async def parse_competitive_url_table(session: aiohttp.ClientSession) -> list[MIPTCompetitiveDev]:
    """"""
    url = "https://pk.mipt.ru/bachelor/2023_decree/2023_decree.php"
    resp = await session.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(await resp.text(), "lxml")
    # parse
    table = soup.find("tbody").find_all("tr")
    raw_data = [await parse_competitive_url_table_row(tr) for tr in table[1:]]
    competitive_groups = await raw_data_to_dc_list(raw_data)

    return competitive_groups


async def parse_competitive_page(session: aiohttp.ClientSession, url: MIPTCompetitiveDev, conn_retries: int = 10) -> list[AbiturSimplified]:
    """"""
    ret = []
    resp = await session.get(url=url.url, headers=HEADERS)
    soup = BeautifulSoup(await resp.text(), "lxml")
    # parse
    body = soup.find("tbody")
    if body is None and conn_retries > 0:
        await asyncio.sleep(2)
        return await parse_competitive_page(session, url, conn_retries - 1)

    body = body.find_all("tr")
    for tr in body:
        tds = tr.find_all("td")
        _, un_str, wet_str, score_str, _, _, cert_str, prior_str, *e = map(lambda x: x.text, tds)

        un = un_str.replace("-", "").replace(" ", "")
        wet = bool(wet_str)
        score = int(score_str)
        cert = cert_str == "Оригинал"
        prior = int(prior_str)

        abitur = AbiturSimplified(unique_code=un, score=score, wet=wet, competitive=url.competitive,
                                  orig_cert=cert, priority=prior, ep_name=f"{url.name} {url.sub_name}")
        ret.append(abitur)

    return ret


async def parse_mipt() -> None:
    """"""
    async with aiohttp.ClientSession() as session:
        urls = await parse_competitive_url_table(session=session)
        mipt_abitur_unpacked = await asyncio.gather(*[asyncio.create_task(parse_competitive_page(session, url))
                                                      for url in urls])
        mipt_abitur = reduce(lambda lst1, lst2: lst1 + lst2, mipt_abitur_unpacked)
        save_to_csv("mipt_abiturs.csv", SAVE_PATH, mipt_abitur, AbiturSimplified)


if __name__ == '__main__':
    asyncio.run(parse_mipt())

# m = MIPTCompetitiveDev(name='01.03.02 Прикладная математика и информатика', sub_name='Прикладная математика и информатика', competitive='budget', url='https://priem.mipt.ru/applications/bachelor_range/%D0%9A%D0%BE%D0%BD%D0%BA%D1%83%D1%80%D1%81%D0%BD%D1%8B%D0%B5%20%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B8%20%D0%9E%D0%B1%D1%89%D0%B8%D0%B5%20%D0%BC%D0%B5%D1%81%D1%82%D0%B0%20(%D0%9F%D1%80%D0%B8%D0%BA%D0%BB%D0%B0%D0%B4%D0%BD%D0%B0%D1%8F%20%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0%20%D0%B8%20%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0_%D0%91%D1%8E%D0%B4%D0%B6%D0%B5%D1%82)%20(HTML).html')
# print(await parse_competitive_page(session, m))

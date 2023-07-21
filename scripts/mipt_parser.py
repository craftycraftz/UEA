import asyncio
import json
from functools import reduce

import aiohttp
from bs4 import BeautifulSoup

from classes import Competitive, EducationalProgram, Abitur, MIPTCompetitiveGroupDev
from config import HEADERS, SAVE_PATH, MIPT_EP_ID_JSON
from database import save_educational_programs, save_abiturs, save_ep_id_to_json
from utlis import save_to_csv


async def parse_edu_progs_row(tr: BeautifulSoup) -> str | tuple | int:
    """"""
    tds = tr.find_all("td")
    tds_text = [td.text.replace("\n", "").replace("\xa0", " ") for td in tds]
    if any(l.isdigit() for l in tds_text[0]) and len(tds_text) == 7:
        # return educational program name
        ret = tds_text[0].split()[0]
        return ret
    elif len(tds_text) == 5 or len(tds_text) == 4 or (len(tds_text) == 7 and tds_text[0] == " "):
        # get target quota places
        if len(tds_text) == 5:
            return int(tds_text[4]) if tds_text[0] != " " else 0
        elif len(tds_text) == 4:
            return int(tds_text[3]) if tds_text[0] != " " else 0
        else:
            return int(tds_text[5]) if tds_text[0] != " " else 0
    elif len(tds_text) == 8:
        # get first program row
        _, name, budget, spe_quota, sep_quota, _, tar_quota, contract = tds_text
    elif len(tds_text) == 4:
        print(tds_text)
    else:
        # get following rows
        name, budget, spe_quota, sep_quota, _, tar_quota, contract = tds_text
    budget, spe_quota, sep_quota, tar_quota, contract = map(lambda x: int(x) if x[0].isdigit() else 0,
                                                            (budget, spe_quota, sep_quota, tar_quota, contract))
    return name, budget, spe_quota, sep_quota, tar_quota, contract


async def parse_edu_progs(session: aiohttp.ClientSession) -> list[EducationalProgram]:
    """"""
    url = "https://pk.mipt.ru/bachelor/2023_places/"
    resp = await session.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(await resp.text(), "lxml")

    rows = soup.find_all("tr")
    code = name = None
    educational_programs = []
    added = set()
    for row in rows[1:-2]:
        row_data = await parse_edu_progs_row(row)
        if isinstance(row_data, str):
            if code is not None and name not in added:
                ep = EducationalProgram(university_name="МФТИ", code=code, name=name, budget_places=budget,
                                        special_quota_places=spe_quota, separate_quota_places=sep_quota,
                                        target_quota_places=tar_quota, contract_places=contract, price=0)
                added.add(name)
                educational_programs.append(ep)
            code = row_data
        elif isinstance(row_data, tuple):
            if name is not None and name not in added:
                ep = EducationalProgram(university_name="МФТИ", code=code, name=name, budget_places=budget,
                                        special_quota_places=spe_quota, separate_quota_places=sep_quota,
                                        target_quota_places=tar_quota, contract_places=contract, price=0)
                added.add(name)
                educational_programs.append(ep)
            name, budget, spe_quota, sep_quota, tar_quota, contract = row_data
        elif isinstance(row_data, int):
            tar_quota += int(row_data)
    ep = EducationalProgram(university_name="МФТИ", code=code, name=name, budget_places=budget,
                            special_quota_places=spe_quota, separate_quota_places=sep_quota,
                            target_quota_places=tar_quota, contract_places=contract, price=0)
    educational_programs.append(ep)

    return educational_programs


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


async def raw_data_to_dc_list(raw: list[tuple[str, list[str | None]] | str]) -> list[MIPTCompetitiveGroupDev]:
    """

    :param raw:
    :return:
    """
    assert isinstance(raw[0], str), "List must starts with educational program name!"
    competitive = {0: Competitive.BUDGET, 1: Competitive.SPECIAL_QUOTA,
                   2: Competitive.SEPARATE_QUOTA, 3: Competitive.TARGET_QUOTA, 4: Competitive.CONTRACT}
    ret = []
    with open(MIPT_EP_ID_JSON) as json_file:
        ep_ids = json.load(json_file)
    for item in raw:
        if isinstance(item, str):
            code = "".join(l for l in item if l.isdigit() or l == ".")
        else:
            name, urls = item
            for i, url in enumerate(urls):
                if url is not None:
                    name = name.replace("\xa0", " ").replace("\n", "").strip()
                    # print(ep_ids["МФТИ"][code])
                    # print(code, name)
                    ep_id = ep_ids["МФТИ"][code][name]
                    ret.append(MIPTCompetitiveGroupDev(
                        code=code,
                        name=name,
                        ep_id=ep_id,
                        competitive=competitive[i],
                        url=url))

    print(f"[INFO] Total urls: {len(ret)}")
    return ret


async def parse_competitive_url_table(session: aiohttp.ClientSession) -> list[MIPTCompetitiveGroupDev]:
    """"""
    url = "https://pk.mipt.ru/bachelor/2023_decree/2023_decree.php"
    resp = await session.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(await resp.text(), "lxml")
    # parse
    table = soup.find("tbody").find_all("tr")
    raw_data = [await parse_competitive_url_table_row(tr) for tr in table[1:]]
    competitive_groups = await raw_data_to_dc_list(raw_data)

    return competitive_groups


async def parse_competitive_page(session: aiohttp.ClientSession, url: MIPTCompetitiveGroupDev, conn_retries: int = 10) -> list[Abitur]:
    """"""
    ret = []
    resp = await session.get(url=url.url, headers=HEADERS)
    soup = BeautifulSoup(await resp.text(), "lxml")
    # parse
    body = soup.find("tbody")
    if body is None and conn_retries > 0:
        await asyncio.sleep(2)
        return await parse_competitive_page(session, url, conn_retries - 1)
    elif body is None and conn_retries <= 0:
        print(f"[WARNING] Cannot process {url=}")  # TODO: replace with log
        return []

    body = body.find_all("tr")
    for tr in body:
        tds = tr.find_all("td")
        if len(tds) == 10 or url.competitive == Competitive.TARGET_QUOTA:
            place, un_str, wet_str, score_str, _, _, cert_str, prior_str, *e = map(lambda x: x.text, tds)
        elif len(tds) == 11:
            place, un_str, _, wet_str, score_str, _, _, cert_str, prior_str, *e = map(lambda x: x.text, tds)
        else:
            print(f"[WARNING] Cannot process {url=}")  # TODO: replace with log
            continue

        wet = bool(wet_str)
        score = int(score_str)
        cert = cert_str == "Оригинал"
        prior = int(prior_str)

        abitur = Abitur(unique_code=un_str, place=place, score=score, wet=wet, competitive=url.competitive,
                        orig_cert=cert, priority=prior, ep_id=url.ep_id)
        ret.append(abitur)
    print(f"[INFO] Parsed {url.ep_id} {url.competitive}")

    return ret


async def parse_mipt() -> None:
    """"""
    async with aiohttp.ClientSession() as session:
        # data = await parse_edu_progs(session)
        # save_educational_programs(data)
        save_ep_id_to_json()

        urls = await parse_competitive_url_table(session=session)
        mipt_abitur_unpacked = await asyncio.gather(*[asyncio.create_task(parse_competitive_page(session, url))
                                                      for url in urls])
        mipt_abitur = reduce(lambda lst1, lst2: lst1 + lst2, mipt_abitur_unpacked)
        print(len(mipt_abitur))
        print("[INFO] Saving to database...")
        save_abiturs(mipt_abitur)
        save_to_csv("mipt_abiturs.csv", SAVE_PATH, mipt_abitur, Abitur)


if __name__ == '__main__':
    asyncio.run(parse_mipt())

# m = MIPTCompetitiveDev(name='01.03.02 Прикладная математика и информатика', sub_name='Прикладная математика и информатика', competitive='budget', url='https://priem.mipt.ru/applications/bachelor_range/%D0%9A%D0%BE%D0%BD%D0%BA%D1%83%D1%80%D1%81%D0%BD%D1%8B%D0%B5%20%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B8%20%D0%9E%D0%B1%D1%89%D0%B8%D0%B5%20%D0%BC%D0%B5%D1%81%D1%82%D0%B0%20(%D0%9F%D1%80%D0%B8%D0%BA%D0%BB%D0%B0%D0%B4%D0%BD%D0%B0%D1%8F%20%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0%20%D0%B8%20%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0_%D0%91%D1%8E%D0%B4%D0%B6%D0%B5%D1%82)%20(HTML).html')
# print(await parse_competitive_page(session, m))

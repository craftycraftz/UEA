import asyncio
from functools import reduce
import aiohttp
from bs4 import BeautifulSoup
from utils import HEADERS, FILEPATH, Product, save_to_csv


async def scraping_page(session: aiohttp.ClientSession, page: int) -> list[str]:
    url = f"https://www.parsemachine.com/sandbox/catalog/?page={page}"
    resp = await session.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(await resp.text(), "lxml")
    cards = soup.find_all("div", class_="card")
    urls = []
    for card in cards:
        href = card.find("a").get("href")
        urls.append(href)

    return urls


async def scraping_product(session: aiohttp.ClientSession, url: str) -> Product:
    resp = await session.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(await resp.text(), "lxml")

    name = soup.find("h1", id="product_name").text.strip()
    description = soup.find("span", id="description").text.replace("\n", " ").strip()
    price = int(soup.find("big", id="product_amount").text.replace(" ", ""))
    article = soup.find("span", id="sku").text
    characteristics = soup.find("table", id="characteristics").find_all("tr")
    width, height, depth = (int(c.find_all("td")[1].text.split()[0]) for c in characteristics)

    return Product(name=name, description=description, link=url, price=price,
                   article=article, width=width, height=height, depth=depth)


async def get_data() -> list[Product]:
    async with aiohttp.ClientSession() as session:
        # get amount of pages
        url = "https://www.parsemachine.com/sandbox/catalog/"
        resp = await session.get(url=url, headers=HEADERS)
        soup = BeautifulSoup(await resp.text(), "lxml")
        pagination_block = soup.find("div", id="pagination")
        amount_of_pages = int(pagination_block.find_all("a")[-2].text)

        # get product page links
        product_urls = await asyncio.gather(*[asyncio.create_task(scraping_page(session, page))
                                              for page in range(1, amount_of_pages + 1)])
        product_urls = reduce(lambda lst1, lst2: lst1 + lst2, product_urls)

        # get products data
        products = await asyncio.gather(
            *[asyncio.create_task(scraping_product(session, f"https://www.parsemachine.com{url}"))
              for url in product_urls])

    return products


def main() -> None:
    products = asyncio.run(get_data())

    save_to_csv(FILEPATH, products)


if __name__ == '__main__':
    from time import time
    start = time()
    main()
    end = time()
    print(f"Total work time for '{__file__}': {end - start:.3f}s")

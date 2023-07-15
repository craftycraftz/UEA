# https://www.parsemachine.com/sandbox/catalog
import requests
from bs4 import BeautifulSoup
from utils import HEADERS, FILEPATH, Product, save_to_csv


def scraping_page(page: int) -> list[str]:
    """

    :param page: page number
    :return: list of products' urls
    """
    url = f"https://www.parsemachine.com/sandbox/catalog/?page={page}"
    resp = requests.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(resp.content, "lxml")
    cards = soup.find_all("div", class_="card")
    urls = []
    for card in cards:
        href = card.find("a").get("href")
        urls.append(href)

    return urls


def scraping_product(url: str) -> Product:
    resp = requests.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(resp.content, "lxml")

    name = soup.find("h1", id="product_name").text.strip()
    description = soup.find("span", id="description").text.replace("\n", " ").strip()
    price = int(soup.find("big", id="product_amount").text.replace(" ", ""))
    article = soup.find("span", id="sku").text
    characteristics = soup.find("table", id="characteristics").find_all("tr")
    width, height, depth = (int(c.find_all("td")[1].text.split()[0]) for c in characteristics)

    return Product(name=name, description=description, link=url, price=price, article=article, width=width,
                   height=height, depth=depth)


def get_data() -> list[Product]:
    # get amount of pages
    url = "https://www.parsemachine.com/sandbox/catalog/"
    resp = requests.get(url=url, headers=HEADERS)
    soup = BeautifulSoup(resp.content, "lxml")
    pagination_block = soup.find("div", id="pagination")
    amount_of_pages = int(pagination_block.find_all("a")[-2].text)

    # get all products' urls
    urls = []
    for page in range(amount_of_pages):
        new_urls = scraping_page(page)
        urls.extend(new_urls)

    # get products' data
    products_data = []
    for url in urls:
        url = f"https://www.parsemachine.com{url}"
        product = scraping_product(url)
        products_data.append(product)

    return products_data


def main() -> None:
    products_data = get_data()
    save_to_csv(FILEPATH, products_data)


if __name__ == '__main__':
    from time import time
    start = time()
    main()
    end = time()
    print(f"Total work time for {__file__}: {end - start:.3f}s")
    # Total work time for C:\Users\Igor\Projects\Test\4_async\scraper_speed_test\synchronous.py: 181.339s


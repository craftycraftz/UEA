import csv
from dataclasses import dataclass


FILEPATH = "product_data.csv"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}


@dataclass
class Product:
    name: str
    description: str
    link: str
    price: int
    article: str
    width: int
    height: int
    depth: int


def save_to_csv(filename: str, data: list[Product]) -> None:
    assert filename.endswith(".csv"), "'filename' must ends with '.csv'."
    with open(filename, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        # write headers
        writer.writerow(list(Product.__annotations__.keys()))
        # write data
        for p in data:
            writer.writerow(list(p.__dict__.values()))

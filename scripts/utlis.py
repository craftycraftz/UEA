import csv
import os


def save_to_csv(filename: str, save_path: str, data: list, save_object: object) -> None:
    assert filename.endswith(".csv"), "'filename' must ends with '.csv'."
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    file_path = os.path.join(save_path, filename)
    with open(file_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.writer(csv_file, delimiter=";")
        # write headers
        writer.writerow(list(save_object.__annotations__.keys()))
        # write data
        for item in data:
            writer.writerow(list(item.__dict__.values()))


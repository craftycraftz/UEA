""""""
import csv
import requests
from bs4 import BeautifulSoup


# get html text
url_old = "https://priem.mipt.ru/applications/bachelor/000000005_%D0%9F%D1%80%D0%B8%D0%BA%D0%BB%D0%B0%D0%B4%D0%BD%D0%B0%D1%8F%20%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0%20%D0%B8%20%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0_%D0%91%D1%8E%D0%B4%D0%B6%D0%B5%D1%82.html"
url = "https://priem.mipt.ru/applications/bachelor_range/%D0%9A%D0%BE%D0%BD%D0%BA%D1%83%D1%80%D1%81%D0%BD%D1%8B%D0%B5%20%D1%81%D0%BF%D0%B8%D1%81%D0%BA%D0%B8%20%D0%9E%D0%B1%D1%89%D0%B8%D0%B5%20%D0%BC%D0%B5%D1%81%D1%82%D0%B0%20(%D0%9F%D1%80%D0%B8%D0%BA%D0%BB%D0%B0%D0%B4%D0%BD%D0%B0%D1%8F%20%D0%BC%D0%B0%D1%82%D0%B5%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0%20%D0%B8%20%D0%B8%D0%BD%D1%84%D0%BE%D1%80%D0%BC%D0%B0%D1%82%D0%B8%D0%BA%D0%B0_%D0%91%D1%8E%D0%B4%D0%B6%D0%B5%D1%82)%20(HTML).html"
response = requests.get(url=url)

# parse
soup = BeautifulSoup(response.content, "lxml")
table = soup.find("table")
# print(table)
html_headers = table.find("thead").find_all("th")
html_info = table.find("tbody").find_all("tr")

# get table headers
headers = [h.text for h in html_headers if len(h.text) > 0]
# get all table info
info = []
for html_row in html_info:
    html_row = html_row.find_all("td")
    row = [html_row[r].text for r in range(len(headers))]
    info.append(row)

# saving data to csv file
with open("mipt_enrollees.csv", "w", encoding="utf-8", newline="") as csv_file:
    writer = csv.writer(csv_file, delimiter=",")
    writer.writerow(headers)
    for row in info:
        writer.writerow(row)

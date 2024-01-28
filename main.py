import random

import requests
from bs4 import BeautifulSoup
import lxml
import json
import csv


headers = {
    "Accept": "*/*",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
}


def get_page(url):
    s = requests.Session()
    response = s.get(url=url, headers=headers)

    with open("index.html", "w", encoding="utf-8") as file:
        file.write(response.text)

    with open("index.html", encoding="utf-8") as file:
        src = file.read()

        soup = BeautifulSoup(src, "lxml")
        all_products_hrefs = soup.find_all(class_="mzr-tc-group-item-href")
        all_categories = {}
        for item in all_products_hrefs:
            item_text = item.text
            item_href = "https://health-diet.ru" + item.get("href")
            all_categories[item_text] = item_href

    with open("all_categories.json", "w", encoding="utf-8") as file:
        json.dump(all_categories, file, indent=4, ensure_ascii=False)


with open("all_categories.json", encoding="utf-8") as file:
    all_categories = json.load(file)
iteration_count = int(len(all_categories)) - 1
count = 0
print(f"Всего итераций: {iteration_count}")
for category_name, category_href in all_categories.items():

    rep = [",", " ", "-", "`"]
    for item in rep:
        if item in category_name:
            category_name = category_name.replace(item, "_")
    req = requests.get(url=category_href, headers=headers)
    src = req.text

    with open(f"data/{category_name}.html", "w", encoding="utf-8") as file:
        file.write(src)

    with open(f"data/{category_name}.html", "r", encoding="utf-8") as file:
        src = file.read()

    soup = BeautifulSoup(src, "lxml")

    alert_block = soup.find(class_="uk-alert-danger")
    if alert_block is not None:
        continue
    table_head = soup.find(class_="mzr-tc-group-table").find("tr").find_all("th")
    product = table_head[0].text
    calories = table_head[1].text
    proteins = table_head[2].text
    fats = table_head[3].text
    carbohydrates = table_head[4].text

    with open(f"data{count}_{category_name}.csv", "w", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow((product, calories, proteins, fats, carbohydrates))

    products_data = soup.find(class_="mzr-tc-group-table").find("tbody").find_all("tr")

    products_info = []
    for item in products_data:
        product_tds = item.find_all("td")
        title = product_tds[0].find("a").text
        calories = product_tds[1].text
        proteins = product_tds[2].text
        fats = product_tds[3].text
        carbohydrates = product_tds[4].text

        products_info.append(
            {
                "Title": title,
                "Calories": calories,
                "Proteins": proteins,
                "Fats": fats,
                "Carbohydrates": carbohydrates,
            }
        )
        with open(f"data{count}_{category_name}.csv", "a", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow((title, calories, proteins, fats, carbohydrates))
    with open(f"data/{count}_{category_name}.json", "a", encoding="utf-8") as file:
        json.dump(products_info, file, indent=4, ensure_ascii=False)
    count = +1
    print(f"Итерация{count}. {category_name} записан.....")
    iteration_count = iteration_count - 1
    if iteration_count == 0:
        print("Парсинг завершен")
        break
    print(f"Осталось итераций: {iteration_count}")


def main():
    get_page(
        url="https://health-diet.ru/table_calorie/?utm_source=leftMenu&utm_medium=table_calorie"
    )


if __name__ == "__main__":
    main()

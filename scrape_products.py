import csv
import requests
import pandas as pd
from bs4 import BeautifulSoup
from urllib3.util import Retry
from requests.adapters import HTTPAdapter


def session_request(url, stream=False):
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    response = session.get(url, stream=stream)
    return response


def get_data():
    """Read category links from csv file and return a csv file products data.
    """
    df = pd.read_csv("categories_links.csv")
    data = []
    link_b = []
    for i in range(len(df)):
        data_raw = list(df.loc[i, :])
        next = data_raw[0]
        while 1:
            response = session_request(next)
            soup = BeautifulSoup(response.text, "html.parser")
            main_div = soup.find(
                "div",
                {
                    "class": "boost-pfs-filter-products product-list product-list--collection"
                },
            )
            items = main_div.find_all(
                "div",
                {
                    "class": "product-item product-item--vertical 1/3--tablet 1/4--lap-and-up"
                },
            )

            for item in items:
                print("Change item")
                item_link = (
                    item.find(
                        "a",
                        {
                            "class": "product-item__image-wrapper product-item__image-wrapper--with-secondary"
                        },
                    )
                    if item.find(
                        "a",
                        {
                            "class": "product-item__image-wrapper product-item__image-wrapper--with-secondary"
                        },
                    )
                    else item.find(
                        "a", {"class": "product-item__title text--strong link"}
                    )
                )
                response_item = session_request(
                    "https://restaurantequipment.com.au" + item_link["href"]
                )
                soup_item = BeautifulSoup(response_item.text, "html.parser")
                main_div = soup_item.find(
                    "div", {"class": "card card--collapsed card--sticky"}
                )
                if not main_div:
                    link_b.append(item_link["href"])
                    break
                sku = (
                    soup_item.find("div", {"class": "product-meta__reference"})
                    .find("span", {"class": "product-meta__sku-number"})
                    .text.strip()
                    if soup_item.find("div", {"class": "product-meta__reference"}).find(
                        "span", {"class": "product-meta__sku-number"}
                    )
                    else None
                )
                card_div = (
                    main_div.find("div", {"class": "card__section"})
                    if main_div
                    else soup.find("div", {"class": "product-meta"})
                )
                upper_card = (
                    card_div.find("div", {"class": "product-meta"})
                    if main_div
                    else card_div
                )
                product_name = upper_card.h1.text.strip() if upper_card.h1 else None
                brand = (
                    upper_card.find("a").find("img")["alt"].strip()
                    if upper_card.find("a") and upper_card.find("a").find("img")
                    else None
                )

                price_div = card_div.find(
                    "div", {"class": "product-form__info-list position__relative"}
                )
                price_sale = (
                    price_div.find(
                        "span", {"class": "price price--highlight display_in"}
                    )
                    .text.split("$")[1]
                    .strip()
                    if price_div.find(
                        "span", {"class": "price price--highlight display_in"}
                    )
                    else None
                )
                price = (
                    price_div.find(
                        "span", {"class": "price price--compare compare_price_set"}
                    )
                    .text.split("$")[1]
                    .strip()
                    if price_div.find(
                        "span", {"class": "price price--compare compare_price_set"}
                    )
                    else None
                )

                description = None
                if soup_item.find("div", {"id": "description"}):
                    description = soup_item.find(
                        "div", {"id": "description"}
                    ).text.strip()
                elif soup.find("div", {"id": "product-description"}):
                    description = soup.find(
                        "div", {"id": "product-description"}
                    ).text.strip()

                data.append(
                    data_raw
                    + [product_name, sku, brand, price_sale, price, description]
                )
            next = soup.find("link", {"rel": "next"})
            if next:
                next = "https://restaurantequipment.com.au" + next["href"]
                print("change next to: ", next)
            else:
                print("change category")
                break

        print("add to csv")
        with open("data.csv", mode="a+", encoding="utf-8") as file:
            writer = csv.writer(file, delimiter=",")
            writer.writerows(data)


if __name__ == "__main__":
    get_data()


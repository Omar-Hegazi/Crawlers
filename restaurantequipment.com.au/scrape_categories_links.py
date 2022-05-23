import csv
import requests
from bs4 import BeautifulSoup


def get_front_bottom(base_url):
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")
    front = soup.find("div", {"class": "collection__meta-inner"}).find("p").text.strip()
    collection_bottom = soup.find("div", {"class": "collection__description"})
    bottom = None
    if collection_bottom:
        bottom_1 = collection_bottom.find("div", {"class": "rte"})
        bottom_2 = None
        if bottom_1:
            bottom_2 = bottom_1.find_all("p", recursive=False)
            bottom = None
            if bottom_2:
                bottom = "\n".join([i.text.strip() for i in bottom_2])
    head = soup.find("div", {"id": "read-more"})
    if head:
        bottom = bottom + "\n" + head.text.strip()
    return front, bottom


def scrape_website_categories(url):
    cnt = []
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    nav_bar = soup.find("div", {"class": "nav-bar__inner"})
    container = nav_bar.find("div", {"class": "container"})
    categories = container.find_all("li", {"class": "nav-bar__item"})[:-1]
    for category in categories:
        category_list = []
        category_info = category.find("a", {"class": "nav-bar__link"})
        category_link = "https://restaurantequipment.com.au/" + category_info["href"]
        category_name = category_info.text.strip()
        front, bottom = get_front_bottom(category_link)
        category_list = [category_link, category_name, front, bottom]
        classes = category.ul.find_all(
            "li", {"class": "nav-dropdown__item"}, recursive=False
        )
        names = []
        for i in classes:
            names.append(i.find("a", {"class": "nav-dropdown__link link"}).text.strip())
        classes = category.find_all("li")
        print(len(classes))
        base = []
        for class_ in classes:
            li_exist = class_.find("a", {"class": "nav-dropdown__link link"})
            if li_exist:
                if li_exist.text.strip() in names:
                    base_name = li_exist.text.strip()
                    base_url = "https://restaurantequipment.com.au" + li_exist["href"]
                    front_class, bottom_class = get_front_bottom(base_url)
                    base = category_list + [
                        base_name,
                        base_url,
                        front_class,
                        bottom_class,
                    ]
                    print("BASE", base_name)
                    if not class_.ul:
                        print("BASE Not", base_name)
                        cnt.append([base_url] + base + [None, None, None, None])
                else:
                    class_url = "https://restaurantequipment.com.au" + li_exist["href"]
                    class_name = li_exist.text.strip()
                    front_class, bottom_class = get_front_bottom(class_url)
                    print("SUBBASE", class_name)
                    cnt.append(
                        [class_url]
                        + base
                        + [class_url, class_name, front_class, bottom_class]
                    )

    with open("categories_links.csv", mode="a+", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(cnt)


if __name__ == "__main__":

    url = "https://restaurantequipment.com.au/?_atid=mm5oOQlUJdEWUpaJK74epixKpZi6yA"
    scrape_website_categories(url)

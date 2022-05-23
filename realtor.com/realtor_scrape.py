import csv
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from selenium import webdriver
from fractions import Fraction
from urllib3.util import Retry
from requests.adapters import HTTPAdapter
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


def selenium_scrape(driver_location):
    """Initalize selenium

    Args:
        driver_location (str): path for chrome_driver

    Returns:
        driver: selenium deriver
    """
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    driver = webdriver.Chrome(driver_location, options=chrome_options)
    return driver


def session_requests(url):
    req_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "accept-encoding": "gzip, deflate, br",
        "accept-language": "en-US,en;q=0.8",
        "upgrade-insecure-requests": "1",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    }
    session = requests.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    response = session.get(url, headers=req_headers)
    return response


data = [
    [
        "properety_url",
        "listing",
        "description",
        "No. of bedrooms",
        "No. of bathrooms",
        "Square foot",
        "Lot size",
        "Sold date",
        "Sold price",
        "Oldest sale date",
        "Oldest sale price",
        "Property address",
        "Longitude",
        "Latitude",
        "Type of home",
        "Year built",
        "Heating data",
        "Cooling data",
        "Total parking spaces",
        "Parking type",
        "Exterior type",
        "Basement",
        "Flooring type",
        "Appliances",
        "Noise level",
        "Floor Factor",
        "Newest tax amount",
        "Newest tax date",
        "Oldest tax amount",
        "Oldest tax date",
    ]
]

page_number = 4
driver = selenium_scrape("C:/chromedriver.exe")
for page in range(1, page_number):
    print(
        f"\n\n ########################## Page Number: {page }############################# \n\n"
    )
    url = f"https://www.realtor.com/realestateandhomes-search/07450/show-recently-sold/pg-{page}"
    response = session_requests(url)
    bs = BeautifulSoup(response.text, "html.parser")
    main_ul = bs.find("ul", {"class": "jsx-343105667 property-list list-unstyle"})
    if main_ul == None:
        continue
    lists_li = main_ul.find_all("li", {"data-testid": "result-card"})
    for list_li in lists_li:
        item = list_li.find("a", {"class": "jsx-1534613990 card-anchor"})
        if item == None or not item.has_attr("href"):
            continue
        item_url = "https://www.realtor.com" + item["href"]
        print(f"item_url: {item_url}   ####")
        driver.get(item_url)
        time.sleep(15)
        # Selenium click buttons
        try:
            main_div = driver.find_element(by=By.ID, value="Property Details")
            button = main_div.find_element(by=By.CLASS_NAME, value="see-more-less")
            driver.execute_script("arguments[0].click();", button)

        except:
            print("Element not found")
        try:
            features_div = driver.find_element(
                by=By.CLASS_NAME, value="styles__CustomPropertyDetails-sc-15j2e83-0"
            )
            button_feature = features_div.find_element(
                by=By.CLASS_NAME, value="rui__b25vpl-1"
            )
            driver.execute_script("arguments[0].click();", button_feature)
        except:
            print("Element not found")
        try:
            taxes_div = driver.find_element(by=By.CLASS_NAME, value="rui__sc-12wjzkx-0")
            button_taxes = taxes_div.find_element(
                by=By.CLASS_NAME, value="rui__b25vpl-1"
            )
            driver.execute_script("arguments[0].click();", button_taxes)
        except:
            print("Element not found")
        try:
            price_div = driver.find_element(by=By.CLASS_NAME, value="rui__ztynyi-0")
            button_price = price_div.find_element(
                by=By.CLASS_NAME, value="rui__b25vpl-1"
            )
            driver.execute_script("arguments[0].click();", button_price)
        except:
            print("Element not found")

        # Parse selenium page with beautifulsoup
        bs_item = BeautifulSoup(driver.page_source, "html.parser")
        listing = bs_item.find("span", {"id": "label-sold"})
        listing_status = listing.text.strip().split(" ")[-1] if listing else None
        print(f"listing_status: {listing_status}   ####")
        description = bs_item.find(
            "div",
            {
                "class": "rui__sc-19ei9fn-0 bStYYc rui__m9gzjc-0 ICydx styles__OverviewText-sc-15j2e83-2 bBSZZw"
            },
        )
        description_text = description.text.strip() if description else None

        no_ul = bs_item.find(
            "ul",
            {
                "class": "rui__sc-19am0y4-0 ktDbox styles__DetailsContainer-sc-1jm502l-1 jxJkOf"
            },
        )
        li_beds_ = (
            no_ul.find("li", {"data-testid": "property-meta-beds"}) if no_ul else None
        )
        li_beds = li_beds_.find("span").text.strip() if li_beds_ else None
        li_baths_ = (
            no_ul.find("li", {"data-testid": "property-meta-baths"}) if no_ul else None
        )
        li_baths = li_baths_.find("span").text.strip() if li_baths_ else None
        li_sqr_foot_ = (
            no_ul.find("li", {"data-testid": "property-meta-sqft"}) if no_ul else None
        )
        li_sqr_foot = (
            li_sqr_foot_.find("span", {"class": "meta-value"}).text.strip()
            if li_sqr_foot_
            else None
        )
        li_lot_size_ = (
            no_ul.find("li", {"data-testid": "property-meta-lot-size"})
            if no_ul
            else None
        )
        li_lot_size = (
            li_lot_size_.find("span", {"class": "meta-value"}).text.strip()
            if li_lot_size_
            else None
        )

        street = bs_item.find(
            "div", {"class": "styles__AddressContainer-sc-1jm502l-0 FfKIi"}
        )
        street_text = (
            street.find("div").text.strip() if street and street.find("div") else None
        )
        print(street_text)
        address = (
            bs_item.find(
                "div", {"class": "styles__Line2-sc-1jm502l-4 ddovWP"}
            ).text.strip()
            if bs_item.find("div", {"class": "styles__Line2-sc-1jm502l-4 ddovWP"})
            else None
        )
        print(address)
        street_address = f"{street_text} {address}" if street_text != address else None
        no_ul_2 = bs_item.find(
            "ul",
            {
                "class": "rui__aqtg6p-0 ijmzeW styles__StyledListingKeyFacts-sc-q2b319-0 goZCjF"
            },
        )
        no_li_2 = no_ul_2.find_all("li") if no_ul_2 else []
        property_type = ""
        year_built = ""
        parking_space = ""
        for i in range(len(no_li_2)):
            li_text = no_li_2[i].span.text.strip().lower()
            if "property type" in li_text:
                property_type = (
                    no_li_2[i]
                    .find(
                        "div",
                        {"class": "rui__sc-19ei9fn-0 bhKNAr rui__sc-163o7f1-0 lkiWPO"},
                    )
                    .text.strip()
                )
            if "year built" in li_text:
                year_built = (
                    no_li_2[i]
                    .find(
                        "div",
                        {"class": "rui__sc-19ei9fn-0 bhKNAr rui__sc-163o7f1-0 lkiWPO"},
                    )
                    .text.strip()
                )
            if "garage" in li_text:
                parking_space = (
                    no_li_2[i]
                    .find(
                        "div",
                        {"class": "rui__sc-19ei9fn-0 bhKNAr rui__sc-163o7f1-0 lkiWPO"},
                    )
                    .text.strip()
                )

        latitude = (
            bs_item.find("meta", {"property": "place:location:latitude"})["content"]
            if bs_item.find("meta", {"property": "place:location:latitude"})
            and bs_item.find("meta", {"property": "place:location:latitude"}).has_attr(
                "content"
            )
            else None
        )
        longitude = (
            bs_item.find("meta", {"property": "place:location:longitude"})["content"]
            if bs_item.find("meta", {"property": "place:location:longitude"})
            and bs_item.find("meta", {"property": "place:location:longitude"}).has_attr(
                "content"
            )
            else None
        )
        price_table_1 = bs_item.find("div", {"class": "rui__ztynyi-0 coyQJd"})

        price_table_2 = price_table_1.find("tbody") if price_table_1 else None
        price_table = price_table_2.find_all("tr") if price_table_2 else None
        newest_price_table = price_table[0].find_all("td") if price_table else None
        newest_price = (
            newest_price_table[2].text.strip() if newest_price_table else None
        )
        newest_price_date = (
            newest_price_table[0].text.strip() if newest_price_table else None
        )
        oldest_price_table = price_table[-1].find_all("td") if price_table else None
        oldest_price = (
            oldest_price_table[2].text.strip() if oldest_price_table else None
        )
        oldest_price_date = (
            oldest_price_table[0].text.strip() if oldest_price_table else None
        )
        back_up = None
        if price_table_1 == None:
            h2 = bs_item.find(
                "h2",
                {
                    "class": "rui__sc-19ei9fn-0 bhKNAr rui__wbiuo8-0 iQocTl styles__StyledTypeDisplay-sc-1smja80-1 dOgJKW"
                },
            )
            if h2:
                back_up = h2.text.strip()
                newest_price
        tax_table_1 = bs_item.find("div", {"class": "rui__sc-12wjzkx-0 hbTFeC"})
        tax_table_2 = tax_table_1.find("tbody") if tax_table_1 else None
        tax_table = tax_table_2.find_all("tr") if tax_table_2 else None
        newest_tax_table = tax_table[0].find_all("td") if tax_table else None
        newest_tax_amount = (
            newest_tax_table[1].text.strip() if newest_tax_table else None
        )
        newest_tax_date = newest_tax_table[0].text.strip() if newest_tax_table else None
        oldest_tax_table = tax_table[-1].find_all("td") if tax_table else None
        oldest_tax_amount = (
            oldest_tax_table[1].text.strip() if oldest_tax_table else None
        )
        oldest_tax_date = oldest_tax_table[0].text.strip() if oldest_tax_table else None

        more_features = bs_item.find("div", {"id": "moreFeatures"})
        h4_features = more_features.find_all("h4") if more_features else []
        ul_features = more_features.find_all("ul") if more_features else None
        noise_level_div = bs_item.find("div", {"class": "rui__sc-1axmkfu-0 ittHGM"})
        noise_level_p = noise_level_div.find("p") if noise_level_div else None
        noise_level = noise_level_p.strong.text.strip() if noise_level_p else None

        flood_factor_div = bs_item.find("div", {"class": "rui__b1iad5-0 kHSZzy"})
        flood_factor_p = flood_factor_div.find_all("p") if flood_factor_div else None
        flood_factor = flood_factor_p[1].strong.text.strip() if flood_factor_p else None
        flood_factor = None if "N/A" in flood_factor else flood_factor
        flood_factor = float(Fraction(flood_factor)) if flood_factor else None
        data.append(
            [
                item_url,
                listing_status,
                li_beds,
                li_baths,
                li_sqr_foot,
                li_lot_size,
                newest_price_date,
                newest_price,
                oldest_price_date,
                oldest_price,
                street_address,
                longitude,
                latitude,
                property_type,
                year_built,
                parking_space,
                noise_level,
                flood_factor,
                newest_tax_amount,
                newest_tax_date,
                oldest_tax_amount,
                oldest_tax_date,
            ]
        )

    with open("realstate.csv", mode="a+", encoding="utf-8") as file:
        writer = csv.writer(file, delimiter=",")
        writer.writerows(data)
        data = []



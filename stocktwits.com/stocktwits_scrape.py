import time
import pytz
import requests
import pandas as pd
from datetime import datetime
from bs4 import BeautifulSoup
from selenium import webdriver
import selenium.webdriver as webdriver
from selenium.webdriver.common.by import By
from PIL import Image, ImageDraw, ImageFont
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def selenium_scrape(driver_location):
    """Define options for selenium driver

    Args:
        driver_location (str): location of the chromedriver

    Returns:
        driver: WebDriver object
    """
    capa = DesiredCapabilities.CHROME
    capa["pageLoadStrategy"] = "none"
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--log-level=3")
    chrome_options.add_argument("--ignore-certificate-errors-spki-list")
    driver = webdriver.Chrome(
        driver_location, options=chrome_options, desired_capabilities=capa
    )

    return driver


def get_timestamp(tz='US/Eastern'):
    """Get timestamp of your timezone

    Args:
        tz (str, optional): Enter your timezone Defaults to 'US/Pacific'.

    Returns:
        str: timestamp
    """
    pdt = pytz.timezone(tz)
    timestamp = datetime.now(pdt).strftime("%m-%d %H:%M %p")
    return timestamp


def send_to_discord(WEBHOOK_URL, file_name):
    """Send file to discord

    Args:
        WEBHOOK_URL (str): URL of the discord webhook
        file_name (str): name of the file to send
    """
    timestamp = get_timestamp()
    csv_name = file_name.split(".")[0]
    text = {"content": f"New update for {csv_name} list \n{timestamp} EST\n"}
    files = {
        "media": open(f"{csv_name}.png", "rb"),
        "file": (file_name, open(file_name, "rb"), "text/csv", {"Expires": "0"})
    }
    requests.post(WEBHOOK_URL, data=text, files=files)


def write_on_image(my_image, csv_file):
    a = pd.read_csv(csv_file)
    file_name = str(csv_file.split(".")[0]).upper()
    full_name = f"{file_name}.png"
    count = 0
    img = Image.open(my_image)
    draw = ImageDraw.Draw(img)
    arialFont = ImageFont.truetype("arial.ttf", 50)
    draw.text((20, 20 + count * 40), file_name, font=arialFont, fill=("black"))
    arialFont = ImageFont.truetype("arial.ttf", 30)
    draw.text((20, 110 + count * 40), "Rank", font=arialFont, fill=("black"))
    draw.text((100, 110 + count * 40), "Symbol",
              font=arialFont, fill=("black"))
    draw.text((220, 110 + count * 40), "Name", font=arialFont, fill=("black"))
    draw.text((820, 110 + count * 40), "Score", font=arialFont, fill=("black"))
    draw.text((970, 110 + count * 40), "Price", font=arialFont, fill=("black"))
    draw.text((1080, 110 + count * 40), "Price%Change",
              font=arialFont, fill=("black"))
    draw.text((1310, 110 + count * 40), "Sentiment",
              font=arialFont, fill=("black"))
    draw.text((1480, 110 + count * 40), "Message Volume",
              font=arialFont, fill=("black"))
    img.save(full_name)
    for i in range(len(a)):  # this is the line that was wrong
        img = Image.open(full_name)
        draw = ImageDraw.Draw(img)
        arialFont = ImageFont.truetype("arial.ttf", 30)
        draw.text((20, 160 + count * 40),
                  str(a.iloc[i, 0]), font=arialFont, fill=("black"))
        draw.text((100, 160 + count * 40),
                  str(a.iloc[i, 1]), font=arialFont, fill=("black"))
        draw.text((220, 160 + count * 40),
                  str(a.iloc[i, 3]), font=arialFont, fill=("black"))
        draw.text((820, 160 + count * 40),
                  str(a.iloc[i, 4]), font=arialFont, fill=("black"))
        draw.text((970, 160 + count * 40),
                  str(a.iloc[i, 5]), font=arialFont, fill=("black"))
        draw.text((1110, 160 + count * 40),
                  str(a.iloc[i, 6]), font=arialFont, fill=("black"))
        draw.text((1310, 160 + count * 40),
                  str(a.iloc[i, 7]), font=arialFont, fill=("black"))
        draw.text((1480, 160 + count * 40),
                  str(a.iloc[i, 8]), font=arialFont, fill=("black"))
        img.save(full_name)
        count += 1
        my_image = full_name


def get_data(driver, url):
    """Scrape data from the url outputs a csv file

    Args:
        driver_location (str): location of the chromedriver
        url (str): link of website to scrape
    """
    print("Getting data from:", url)
    driver.set_page_load_timeout(30)
    n = -1
    while n == -1:
        driver.get(url)
        time.sleep(30)
        csv_name = url.split("/")[-1]
        soup = BeautifulSoup(driver.page_source, "html.parser")
        raws = soup.find_all("tr", class_="st_PaKabGw st_1jzr122")
        if raws == []:
            n = -1
        else:
            n = 1
    symbol_links = driver.find_elements(
        by=By.XPATH, value="//a[@class='st_8Yt1YyC st_25h4Pte']"
    )
    for link in symbol_links:
        link.send_keys(Keys.CONTROL + Keys.RETURN)
    time.sleep(30)

    cnt = len(driver.window_handles) - 1
    handles = driver.window_handles[1:]
    list_dict = []
    for index in range(len(raws)):
        print("Scraping data for item:", index + 1)
        td = raws[index].find_all("td")
        if td == None:
            print("Rerun script")
            break
        rank = td[0].text.strip()
        sympol = td[1].text.strip()

        driver.switch_to.window(driver.window_handles[cnt])
        cnt -= 1
        soup_sympol = BeautifulSoup(driver.page_source, "html.parser")
        sympol_link = driver.current_url
        sentiment_message = soup_sympol.find_all(
            "div", class_="st_21nJvQl st_2h5TkHM st_8u0ePN3 st_2mehCkH"
        )
        message_volume = None
        sentiment = None
        if len(sentiment_message) > 0:
            sentiment = sentiment_message[1].text.strip()
            svg_sentiment = sentiment_message[1].find('svg')
            svg_sentiment = svg_sentiment.find(
                'path')['d'] if svg_sentiment else None
            if svg_sentiment and svg_sentiment[0] == 'M':
                sentiment = f"-{sentiment}"
            if svg_sentiment and svg_sentiment[0] == 'm':
                sentiment = f"+{sentiment}"

            message_volume = sentiment_message[2].text.strip()
            svg_message = sentiment_message[2].find('svg')
            svg_message = svg_message.find(
                'path')['d'] if svg_message else None
            if svg_message and svg_message[0] == 'M':
                message_volume = f"-{message_volume}"
            if svg_message and svg_message[0] == 'm':
                message_volume = f"+{message_volume}"

        name = td[2].text.strip()
        score = td[3].text.strip()
        price = td[4].text.strip()
        price_change_obj = td[5]
        path = price_change_obj.find("path")['d']
        price_change = price_change_obj.text.strip()
        if path[0] == 'M':
            price_change = f"-{price_change}"
        if path[0] == 'm':
            price_change = f"+{price_change}"

        dict_raw = {
            "Rank": rank,
            "Symbol": sympol,
            "Sympol_Link": sympol_link,
            "Name": name,
            "Score": score,
            "Price": price,
            "Price%Change": price_change,
            "Sentiment": sentiment,
            "Message_Volume": message_volume
        }
        list_dict.append(dict_raw)

    print("############################")
    df = pd.DataFrame(list_dict)
    df.to_csv(csv_name + ".csv", index=False)

    for handle in handles:
        driver.switch_to.window(handle)
        driver.close()
    driver.switch_to.window(driver.window_handles[0])


if __name__ == "__main__":
    """Run script
    You have to variables to be able to run the code
    driver_location (str): location of the chromedriver
    WEBHOOK_URL (str): link of the webhook
    """
    driver_location = "C:/chromedriver.exe"
    WEBHOOK_URL = "ADD DISCORD WEBHOOK URL HERE"
    urls = [
        "https://stocktwits.com/rankings/trending",
        "https://stocktwits.com/rankings/most-active",
        "https://stocktwits.com/rankings/watchers",
    ]

    driver = selenium_scrape(driver_location)
    for url in urls:
        get_data(driver, url)

    driver.quit()

    for url in urls:
        csv_file = url.split("/")[-1] + ".csv"
        write_on_image('image.png', csv_file)
        send_to_discord(WEBHOOK_URL, csv_file)

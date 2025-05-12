import cloudscraper
import random
import string
import json
from datetime import datetime
import requests
import sys

# This is a link used to get the prices shown for MP sellers on an item's backpack.tf page.
# It's technically an API endpoint but is still cloudflare protected, regardless this felt more consistant than actually scraping MP
KEY_PAGE_URL = "https://backpack.tf/item/get_third_party_prices/Unique/Mann%20Co.%20Supply%20Crate%20Key/Tradable/Craftable"


def generate_random_cookie():
    """
    Generates a 20 letter cookie, as BP just needs a user-id cookie to exist in the request to allow it through
    """
    return "".join(random.choice(string.ascii_letters + string.digits) for _ in range(20))


def update_key_price():
    with open("key_prices.json", "r") as f:
        key_prices = json.load(f)
    try:
        scraper = cloudscraper.create_scraper()
        cookies = {
            "user-id": generate_random_cookie(),
        }
        response = scraper.get(KEY_PAGE_URL, cookies=cookies)
        response.raise_for_status()
        price_data = response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to get valid response from API: {e}")
        sys.exit(1)

    raw_key_price = float(price_data["prices"]["mp"]["lowest_price"].replace("$", ""))
    today = datetime.today().strftime("%Y-%m-%d")
    key_prices[today] = raw_key_price

    with open("key_prices.json", "w") as f:
        json.dump(key_prices, f)


if __name__ == "__main__":
    update_key_price()

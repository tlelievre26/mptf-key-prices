import json
from datetime import datetime, timedelta
from glob import glob
import os
import pandas as pd
from collections import defaultdict


def find_missing_dates(date_list):
    """
    Find missing dates in a list of YYYY-MM-DD formatted dates
    """
    # Convert string dates to datetime objects
    dates = [datetime.strptime(date_str, "%Y-%m-%d").date() for date_str in date_list]

    # Find min and max dates
    min_date = min(dates)
    max_date = max(dates)

    # Create a set of all existing dates for O(1) lookups
    date_set = set(dates)

    # Generate a list of all dates in the range
    delta = max_date - min_date
    all_dates = [min_date + timedelta(days=i) for i in range(delta.days + 1)]

    # Find missing dates
    missing_dates = [d.strftime("%Y-%m-%d") for d in all_dates if d not in date_set]

    return missing_dates


def parse_existing_files():
    """
    Use the assorted data I've collected to build a starting data file for this script
    """
    if not os.path.exists("key_prices.json"):
        # Process the assorted data files I've collected
        with open("2017-2019.json", "r") as f:
            data1 = json.load(f)

        with open("2019-2023.json", "r") as f:
            data2 = json.load(f)

        with open("Feb2025-May2025.json") as f:
            data3 = json.load(f)

        key_prices = dict()
        for date, vals in data1.items():
            key_prices[date] = round(sum(vals.values()) / len(vals), 2)
        key_prices.update(data2["marketplace.tf"])

        for i, price in enumerate(data3["prices"]):
            sale_date = datetime.strptime(data3["dates"][i], "%b %d, %Y").strftime("%Y-%m-%d")
            key_prices[sale_date] = price

    else:
        with open("key_prices.json", "r") as f:
            key_prices = json.load(f)

    key_sales = defaultdict(list)
    csv_files = glob(os.path.join("sales_data", "*.csv"))
    for file_path in csv_files:
        df = pd.read_csv(file_path)
        key_sale_rows = df[df["sku"] == "5021;6"]
        for _, row in key_sale_rows.iterrows():
            sale_date = datetime.strptime(row["date"], "%d %B, %Y %H:%M").strftime("%Y-%m-%d")
            # I'll use the files provided by manic as ground truth
            if not sale_date in key_prices:
                key_sales[sale_date].append(row["price"])

    for date, sales in key_sales.items():
        key_prices[date] = round(sum(sales) / len(sales), 2)

    missing_dates = find_missing_dates(list(key_prices.keys()))
    print(f"{len(missing_dates)} days of sale data are currently missing")
    with open("key_prices.json", "w") as f:
        json.dump(key_prices, f)


if __name__ == "__main__":
    parse_existing_files()

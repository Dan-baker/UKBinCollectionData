from bs4 import BeautifulSoup
from get_bin_data import AbstractGetBinDataClass
from datetime import datetime

import pandas as pd
import re


class CouncilClass(AbstractGetBinDataClass):
    """
    Concrete classes have to implement all abstract operations of the
    baseclass. They can also override some
    operations with a default implementation.
    """

    def parse_data(self, page: str) -> dict:
        # Make a BS4 object
        soup = BeautifulSoup(page.text, features="html.parser")
        soup.prettify()

        data = {"bins": []}
        month_class_name = 'class="eventmonth"'
        regular_collection_class_name = "collectiondate regular-collection"
        holiday_collection_class_name = "collectiondate bankholiday-change"
        regex_string = "[^0-9]"

        calendar_collection = soup.find("ol", {"class": "nonumbers news collections"})
        calendar_list = calendar_collection.find_all("li")
        current_month = ""
        current_year = ""

        for element in calendar_list:
            element_tag = str(element)
            if month_class_name in element_tag:
                current_month = datetime.strptime(element.text, "%B %Y").strftime("%m")
                current_year = datetime.strptime(element.text, "%B %Y").strftime("%Y")
            elif regular_collection_class_name in element_tag:
                week_value = element.find_next("span", {"class": f"{regular_collection_class_name}"})
                day_of_week = re.sub(regex_string, "", week_value.text).strip()
                collection_date = datetime(int(current_year), int(current_month), int(day_of_week)).strftime("%d/%m/%Y")
                collections = week_value.find_next_siblings("span")
                for item in collections:
                    x = item.text
                    bin_type = item.text.strip()
                    if len(bin_type) > 1:
                        dict_data = {
                            "type":           bin_type,
                            "collectionDate": collection_date,
                        }
                        data["bins"].append(dict_data)
            elif holiday_collection_class_name in element_tag:
                week_value = element.find_next("span", {"class": f"{holiday_collection_class_name}"})
                day_of_week = re.sub(regex_string, "", week_value.text).strip()
                collection_date = datetime(int(current_year), int(current_month), int(day_of_week)).strftime("%d/%m/%Y")
                collections = week_value.find_next_siblings("span")
                for item in collections:
                    x = item.text
                    bin_type = item.text.strip()
                    if len(bin_type) > 1:
                        dict_data = {
                            "type":           bin_type + " (bank holiday replacement)",
                            "collectionDate": collection_date,
                        }
                        data["bins"].append(dict_data)
        return data

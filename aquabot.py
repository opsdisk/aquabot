#!/usr/bin/env python

# Standard Python libraries.
import datetime
import json
import logging
import os
import time

# Third party Python libraries.
import requests
from bs4 import BeautifulSoup
from TwitterAPI import TwitterAPI

# Custom Python libraries.


# Setup logging
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
rootLogger = logging.getLogger()


class Aquifer:
    def __init__(self):
        self.sleeptime = 600  # In seconds
        self.url = "https://data.edwardsaquifer.org/j-17.php"
        self.successful_update = False
        self.todays_date = datetime.date.today()
        self.retrieve_twitter_creds()

    def run(self):
        while True:
            if (
                (900 < self.current_time())  # Is it after 9:00 AM CST?
                and (self.todays_date < self.retrieve_todays_date())  # Is it the next day?
                and (not self.successful_update)
            ):  # Was an update successful today?

                today_water_level, yesterday_water_level, ten_day_average = self.fetch_levels()
                message = "The J-17 Bexar aquifer level is {}. Yesterday, it was {} and the 10-day average is {}".format(
                    today_water_level, yesterday_water_level, ten_day_average
                )

                # Update Twitter
                self.post_tweet(message)

                # Update variables
                self.todays_date = self.retrieve_todays_date()
                self.successful_update = True

            else:
                rootLogger.info("[*] Sleeping for {} seconds...".format(self.sleeptime))
                time.sleep(self.sleeptime)
                self.successful_update = False

    def fetch_levels(self):
        rootLogger.info("[*] Fetching water levels...")

        headers = {"User-Agent": "Edwards Aquifer Bot - Follow on Twitter: @edwardsaquabot"}

        response = requests.get(self.url, headers=headers, verify=True, timeout=60)
        if response.status_code != 200:
            rootLogger.error(
                "HTTP status code: {} -- unsuccessfully retrieved: {}".format(response.status_code, self.url)
            )
            return

        # Use beautiful soup to grab the levels...works, maybe not the best though.
        soup = BeautifulSoup(response.text, "html.parser")
        table = soup.find_all("table")[1]

        # Today's Reading.
        column = table.find_all("td")[0]
        today_water_level = column.find("span").contents[0].strip()

        # Yesterday's Reading.
        column = table.find_all("td")[2]
        yesterday_water_level = column.find("span").contents[0].strip()

        # 10 Day Average Reading.
        column = table.find_all("td")[4]
        ten_day_average = column.find("span").contents[0].strip()

        return today_water_level, yesterday_water_level, ten_day_average

    def current_time(self):
        now = time.localtime()
        hour_min = int(time.strftime("%H%M", now))
        rootLogger.info("[*] Current time: {}".format(hour_min))
        return hour_min

    def retrieve_todays_date(self):
        todays_date = datetime.date.today()
        rootLogger.info("[*] Today's date: {}".format(todays_date))
        return todays_date

    def retrieve_twitter_creds(self):
        with open("twitter_creds.json", "r") as json_file:
            self.twitter_creds = json.loads(json_file.read())

    def post_tweet(self, message):
        twitter = TwitterAPI(
            self.twitter_creds["consumerKey"],
            self.twitter_creds["consumerSecret"],
            self.twitter_creds["accessToken"],
            self.twitter_creds["accessTokenSecret"],
        )
        request = twitter.request("statuses/update", {"status": message})
        status_code = request.status_code
        if status_code == 200:
            rootLogger.info("Successfully tweeted: {}".format(message))
        else:
            rootLogger.error("HTTP status code: {} -- unsuccessfully tweeted: {}".format(status_code, message))


def log_timestamp():
    now = time.localtime()
    timestamp = time.strftime("%Y%m%d_%H%M%S", now)
    return timestamp


if __name__ == "__main__":

    rootLogger.setLevel(20)  # INFO

    # Log file handling
    fileHandler = logging.FileHandler("{}_{}_PID-{}.log".format(__file__.strip(".py"), log_timestamp(), os.getpid()))
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)

    # Console logging
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)

    aq = Aquifer()
    aq.run()

#### Introduction
Here in South Texas, outside water usage is dictated by the water level in the Edwards Aquifer, "a unique groundwater system and one of the most prolific artesian aquifers in the world" (https://en.wikipedia.org/wiki/Edwards_Aquifer).  Home owners can only water their grass on certain days and times depending on the water restriction stage.  The water restriction stage is determined by the level in the Edwards Aquifer.  Instead of visiting the water level website everyday, I wanted to play around with the Twitter API to scrape the aquifer water level data, then tweet it out from the [@edwardsaquabot](https://twitter.com/edwardsaquabot) account!

#### Logging
I used this project to get familiar with the Python `logging` module that is used to print to the console as well as a .log file.

```python
# Setup logging
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
rootLogger = logging.getLogger()
```
```python
if __name__ == "__main__":

    rootLogger.setLevel(20)  # INFO
    
    # Log file handling
    fileHandler = logging.FileHandler(__file__.strip(".py") + "_" + log_timestamp() + "_PID-" + str(os.getpid()) + ".log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    
    # Console logging
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
```  

#### Fetching Water Levels
The water levels can be found here, [http://data.edwardsaquifer.org/j-17.php](http://data.edwardsaquifer.org/j-17.php), so that page is scraped using BeatifulSoup, a HTML parser. The `fetch_levels` function retrieves the relevant information:

```python
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
```

The [TwitterAPI](https://github.com/geduldig/twitterapi) Python module loads the account details, authenticates, and posts the results.  The first step is to parse the credentials in the twitter_creds.json file.  Note that the `twitter_creds.json` in the code must be populated with your specific API credentials.

```python
def retrieve_twitter_creds(self):
    with open("twitter_creds.json", "r") as json_file:
        self.twitter_creds = json.loads(json_file.read())
```

Post the information to Twitter.

```python
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
```

#### Conclusion
All of the code can be found on the Opsdisk Github repository here: https://github.com/opsdisk/aquabot.  Comments, suggestions, and improvements are always welcome.  Be sure to follow [@opsdisk](https://twitter.com/opsdisk) on Twitter for the latest updates. 
 
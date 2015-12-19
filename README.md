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
The water levels can be found here, [http://data.edwardsaquifer.org/j-17.php](http://data.edwardsaquifer.org/j-17.php), so that page is scraped using BeatifulSoup, a HTML parser. The `fetch_level` function retrieves the relevant information:

```python
def fetch_level(self):
        # Use beautiful soup to grab the levels...works, maybe not the best though
        rootLogger.info("[*] Fetching water levels...")
        page = urllib2.urlopen(self.url)
        soup = BeautifulSoup(page.read())
        table = soup.find_all('table')[1]
        
        # Today's Reading
        column = table.find_all('td')[0]
        todayWaterLevel = column.find('span').contents[0].strip()

        # Yesterday's Reading
        column = table.find_all('td')[2]
        yesterdayWaterLevel = column.find('span').contents[0].strip()     
        
        # 10 Day Average Reading
        column = table.find_all('td')[4]
        tenDayAverage = column.find('span').contents[0].strip()  

        return todayWaterLevel, yesterdayWaterLevel, tenDayAverage
```
The [TwitterAPI](https://github.com/geduldig/twitterapi) Python module loads the account details, authenticates, and posts the results.  The first step is to parse the credentials in the TwitterAPI_creds.ini file using ConfigParser.  Note that the `TwitterAPI_creds.ini` in the code must be populated with your specific API credentials.

```python
    def parse_twitter_creds(self):
        parser = SafeConfigParser()
        parser.read('TwitterAPI_creds.ini')
        self.consumerKey = parser.get('creds', 'consumerKey')
        self.consumerSecret = parser.get('creds', 'consumerSecret')
        self.accessToken = parser.get('creds', 'accessToken')
        self.accessTokenSecret = parser.get('creds', 'accessTokenSecret')

```

Post the information to Twitter.

```python
    def post_tweet(self, message):
        twitter = TwitterAPI(self.consumerKey, self.consumerSecret, self.accessToken, self.accessTokenSecret)
        request = twitter.request('statuses/update', {'status': message})
        statusCode = request.status_code
        if statusCode == 200:
            rootLogger.info("Successfully tweeted: {0}".format(message))
        else:
            rootLogger.error("HTTP status code: {0} -- unsuccessfully tweeted: {1}".format(statusCode, message))
```

#### Conclusion
All of the code can be found on the Opsdisk Github repository here: https://github.com/opsdisk/aquabot.  Comments, suggestions, and improvements are always welcome.  Be sure to follow [@opsdisk](https://twitter.com/opsdisk) on Twitter for the latest updates. 
 
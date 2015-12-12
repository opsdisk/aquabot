#!/usr/bin/env python
import datetime
import logging
import os
import time
import urllib2

from bs4 import BeautifulSoup
from ConfigParser import SafeConfigParser
from TwitterAPI import TwitterAPI

# Setup logging
logFormatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
rootLogger = logging.getLogger()


class Aquifer():

    def __init__(self):
        self.sleeptime = 600  # In seconds
        self.url = "http://data.edwardsaquifer.org/j-17.php"
        self.sucUpdate = False
        self.todaysDate = datetime.date.today()
        self.parse_twitter_creds()

    def run(self):
        while True:
            if ((900 < self.current_time())  # Is it after 9:30 AM CST?
                    and (self.todaysDate < self.todays_date())  # Is it the next day?
                    and (not self.sucUpdate)):  # Was an update successful today?
                
                todayWaterLevel, yesterdayWaterLevel, tenDayAverage = self.fetch_level()
                message = "The J-17 Bexar aquifer level is " + todayWaterLevel + "'. Yesterday, it was " + yesterdayWaterLevel + "' and the 10-day average is " + tenDayAverage + "'"
                # print message
                # Update Twitter
                self.post_tweet(message)

                # Update variables
                self.todaysDate = self.todays_date()
                self.sucUpdate = True
                
            else:
                #print "[*] Sleeping for " + str(self.sleeptime) + " seconds..."
                rootLogger.info("[*] Sleeping for {0} seconds...".format(self.sleeptime))
                time.sleep(self.sleeptime)
                self.sucUpdate = False
    
    def fetch_level(self):
        # Use beautiful soup to grab the levels...works, maybe not the best though
        #print "[*] Fetching water level..."
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
        
    def current_time(self):
        now = time.localtime()
        hourMin = int(time.strftime('%H%M', now))
        #print "[*] Current time: " + str(int(time.strftime('%H%M', now)))
        rootLogger.info("[*] Current time: {0}".format(hourMin))
        return hourMin
  
    def todays_date(self):
        todaysDate = datetime.date.today()
        #print "[*] Today's date: " + str(todaysDate)
        rootLogger.info("[*] Today's date: {0}".format(todaysDate))
        return todaysDate
        
    def parse_twitter_creds(self):
        parser = SafeConfigParser()
        parser.read('TwitterAPI_creds.ini')
        self.consumerKey = parser.get('creds', 'consumerKey')
        self.consumerSecret = parser.get('creds', 'consumerSecret')
        self.accessToken = parser.get('creds', 'accessToken')
        self.accessTokenSecret = parser.get('creds', 'accessTokenSecret')
    
    def post_tweet(self, message):
        twitter = TwitterAPI(self.consumerKey, self.consumerSecret, self.accessToken, self.accessTokenSecret)
        request = twitter.request('statuses/update', {'status': message})
        statusCode = request.status_code
        if statusCode == 200:
            rootLogger.info("Successfully tweeted: {0}".format(message))
        else:
            rootLogger.error("HTTP status code: {0} -- unsuccessfully tweeted: {1}".format(statusCode, message))
        
        
def log_timestamp():
    now = time.localtime()
    timestamp = time.strftime('%Y%m%d_%H%M%S', now)
    return timestamp
           
if __name__ == "__main__":

    '''Official Edwards level (J-17 Bexar index well) readings are updated on this page between 9:30 a.m. and noon, Monday through Friday.'''
    
    rootLogger.setLevel(20)  # INFO
    
    # Log file handling
    fileHandler = logging.FileHandler(__file__.strip(".py") + "_" + log_timestamp() + "_PID-" + str(os.getpid()) + ".log")
    fileHandler.setFormatter(logFormatter)
    rootLogger.addHandler(fileHandler)
    
    # Console logging
    consoleHandler = logging.StreamHandler()
    consoleHandler.setFormatter(logFormatter)
    rootLogger.addHandler(consoleHandler)
    
    aq = Aquifer()
    aq.run()   
import os

my_secret = os.environ['api_key']

import requests
from bs4 import BeautifulSoup
import pandas as pd
import io
from alpha_vantage.timeseries import TimeSeries


#monthly data of Microsoft

ts1 = TimeSeries(key = my_secret)

ts1.get_monthly("MSFT")

#weekly data of Microsoft

ts2 = TimeSeries(key = my_secret)

ts2.get_weekly("MSFT")



#income statement for Microsoft
url = "https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol=MSFT&apikey=my_secret"

r = requests.get(url)

fd = BeautifulSoup(r.content)

print(fd)

#Bollinger bands for Microsoft

url = "https://www.alphavantage.co/query?function=BBANDS&symbol=MSFT&interval=daily&time_period=10&series_type=open&nbdevup=3&nbdevdn=3&apikey=my_secret"
r = requests.get(url)
ti = BeautifulSoup(r.content)

print(ti)

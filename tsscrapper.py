from bs4 import BeautifulSoup
import requests
import json
import re
import datetime

response = requests.request("GET", "http://124.124.103.93/COVID/home.htm")
soup = BeautifulSoup(response.content, 'html5lib')
table = soup.find_all("div", {"class": "cube-count"})
print(table)

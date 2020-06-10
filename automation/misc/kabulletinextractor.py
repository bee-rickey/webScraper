import requests
import pdftotext
import re
from bs4 import BeautifulSoup



response = requests.request("GET", "https://covid19.karnataka.gov.in/new-page/Health%20Department%20Bulletin/en")
soup = BeautifulSoup(response.content, 'html5lib')

rows = soup.find_all("td")

for row in rows:
	aTag = row.find("a")
	if aTag is not None:
		if 'karnataka.gov' in aTag['href']:
			fileNameArray = aTag['href'].split('/')
			fileName = fileNameArray[len(fileNameArray) - 1]
			r = requests.get(aTag['href'], allow_redirects=True)
			open("KABulletin/" + fileName, 'wb').write(r.content)

from bs4 import BeautifulSoup
import requests
import json
import re
import datetime
import codecs
from ast import literal_eval

def getAPDelta():
	nameMapping = {}
	stateDashboard = requests.request("get", "https://health.odisha.gov.in/js/distDtls.js")
	covidDashboard = requests.request("get", "https://api.covid19india.org/state_district_wise.json").json()
	orData = covidDashboard['Odisha']['districtData']

	string = re.sub('var districtdetails =', '', stateDashboard.content.decode("utf-8-sig"))
	string = re.sub('//.*', '', string)
#print(string)
	districtData = json.loads((string))
	print(type(districtData))

	'''for obj in districtData:
		print(obj)
       '''



#			outputString += "," + str(data.get_text() - orData[districtName]['confirmed'])



				

getAPDelta()

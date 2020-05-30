from bs4 import BeautifulSoup
from deltaCalculator import DeltaCalculator
import requests
import sys
import json
import os
import re
import datetime
import logging
import argparse

logging.basicConfig(filename='deltaCalculator.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
deltaCalculator = DeltaCalculator()
metaDictionary = {}
option = ""


class AutomationMeta:
	def __init__(self, stateName, stateCode, url):
		self.stateName = stateName
		self.stateCode = stateCode
		self.url = url

def fetchData(stateName):
	if stateName == "All States":
		for key, metaObject in metaDictionary.items():
			logging.info("Calling delta calculator for: " + metaObject.stateCode)
			eval(metaObject.stateCode + "GetData()")
	else:
		logging.info("Calling delta calculator for: " + metaDictionary[stateName].stateCode)
		eval(metaDictionary[stateName].stateCode + "GetData()")


def loadMetaData():
	with open("automation.meta", "r") as metaFile:
		for line in metaFile:
			lineArray = line.strip().split(',') 
			metaObject = AutomationMeta(lineArray[0].strip(), lineArray[1].strip(), lineArray[2].strip())
			metaDictionary[lineArray[0].strip()] = metaObject

def APGetData():
	stateDashboard = requests.request("post", "http://covid19.ap.gov.in/Covid19_Admin/api/CV/DashboardCountAPI").json()

	districtArray = []
	for districtDetails in (stateDashboard['cases_district']):
		districtDictionary = {}
		districtDictionary['districtName'] =  districtDetails['district_name']
		districtDictionary['confirmed'] =  int(districtDetails['cases'])
		districtDictionary['recovered'] =  int(districtDetails['recovered'])
		districtDictionary['deceased'] =  int(districtDetails['death'])

		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Andhra Pradesh", districtArray, option)

def ORGetData():
	stateDashboard = requests.request("get", "https://health.odisha.gov.in/js/distDtls.js")
	os.system("curl -sk https://health.odisha.gov.in/js/distDtls.js | grep -i 'District_id' | sed 's/\"//g' | sed 's/,/:/g'| cut -d':' -f4,8,12,14,18,22 |sed 's/:/,/g' > orsite.csv")

	districtArray = []
	with open("orsite.csv", "r") as metaFile:
		for line in metaFile:
			districtDictionary = {}
			lineArray = line.strip().split(',') 
			districtDictionary['districtName'] = lineArray[0].strip()
			districtDictionary['confirmed'] = int(lineArray[1].strip())
			districtDictionary['recovered'] = int(lineArray[2].strip())
			districtDictionary['deceased'] = int(lineArray[3].strip())
		
			districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Odisha", districtArray, option)


def MHGetData():
	stateDashboard = requests.request("get", "https://services5.arcgis.com/h1qecetkQkV9PbPV/arcgis/rest/services/COVID19_Location_Summary/FeatureServer/0/query?f=json&where=1%3D1&returnGeometry=false&spatialRel=esriSpatialRelIntersects&outFields=*").json()

	districtArray = []
	for districtDetails in stateDashboard['features']:
		districtDictionary = {}
		districtDictionary['districtName'] = districtDetails['attributes']['District']
		districtDictionary['confirmed'] = districtDetails['attributes']['Positive']
		districtDictionary['recovered'] = districtDetails['attributes']['Recovered']
		districtDictionary['deceased'] = districtDetails['attributes']['Death']
		districtArray.append(districtDictionary)

	print(option)
	deltaCalculator.getStateDataFromSite("Maharashtra", districtArray, option)
		

def RJGetData():
	response = requests.request("GET", "http://www.rajswasthya.nic.in/")
	soup = BeautifulSoup(response.content, 'html5lib')
	table = soup.find('blockquote').find('table').find_all('tr')


	districtArray = []
	for index, rowContent in enumerate(table):
		dataPoints = rowContent.find_all("td")
		if index == 0 or len(dataPoints) != 7:
			continue
		districtName = re.sub(' +', ' ', re.sub('\n', ' ', dataPoints[1].get_text().strip()))

		districtDictionary = {}
		districtDictionary['districtName'] = districtName
		districtDictionary['confirmed'] = int(dataPoints[4].get_text().strip())
		districtDictionary['recovered'] = int(dataPoints[5].get_text().strip())
		districtDictionary['deceased'] = -999
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Rajasthan", districtArray, option)


def GJGetData():
  print("GJ")

def TSGetData():
  print("TS")

def UPGetData():
  print("UP")

def main():

	loadMetaData()
	stateName = ""

	if len(sys.argv) > 1:
		stateName = sys.argv[1]

	global option 
	if len(sys.argv) == 3:
		option = sys.argv[2]

	if not stateName:
		stateName = "All States"
	fetchData(stateName)

if __name__ == '__main__':
	main()

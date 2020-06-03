#!/usr/bin/python3
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
			print("Dashboard url: " + metaObject.url)
	else:
		logging.info("Calling delta calculator for: " + metaDictionary[stateName].stateCode)
		eval(metaDictionary[stateName].stateCode + "GetData()")
		print("Dashboard url: " + metaDictionary[stateName].url)


def loadMetaData():
	with open("automation.meta", "r") as metaFile:
		for line in metaFile:
			if line.startswith('#'):
				continue
			lineArray = line.strip().split(',') 
			metaObject = AutomationMeta(lineArray[0].strip(), lineArray[1].strip(), lineArray[2].strip())
			metaDictionary[lineArray[0].strip()] = metaObject

def APGetData():
	stateDashboard = requests.request("post", metaDictionary['Andhra Pradesh'].url).json()

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
	stateDashboard = requests.request("get", metaDictionary['Maharashtra'].url).json()

	districtArray = []
	for districtDetails in stateDashboard['features']:
		districtDictionary = {}
		districtDictionary['districtName'] = districtDetails['attributes']['District']
		districtDictionary['confirmed'] = districtDetails['attributes']['Positive']
		districtDictionary['recovered'] = districtDetails['attributes']['Recovered']
		districtDictionary['deceased'] = districtDetails['attributes']['Death']
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Maharashtra", districtArray, option)
		

def RJGetData():
	response = requests.request("GET", metaDictionary['Rajasthan'].url)
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
	response = requests.request("GET", metaDictionary['Gujarat'].url)
	soup = BeautifulSoup(response.content, 'html5lib')
	table = soup.find("tbody").find_all("tr")
	
	districtArray = []
	for index, row in enumerate(table):
		if index == len(table) - 1:
			continue
    	
		dataPoints = row.find_all("td")
		districtDictionary = {}
		districtDictionary['districtName'] = dataPoints[0].get_text()
		districtDictionary['confirmed'] = int(dataPoints[1].get_text().strip())
		districtDictionary['recovered'] = int(dataPoints[3].get_text().strip())
		districtDictionary['deceased'] = int(dataPoints[5].get_text().strip())
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Gujarat", districtArray, option)


def TSGetData():
  print("TS")

def UPGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	secondRunArray = []
	masterColumnList = ""
	masterColumnArray = []
	splitArray = []
	with open("up1.txt", "r") as upFile:
		for line in upFile:
			splitArray = re.sub('\n', '', line.strip()).split('|')
			linesArray = splitArray[0].split(',')
			columnList = splitArray[1].split(',')

			if len(linesArray) != 8 or len(columnList) != 8:
				secondRunArray.append(linesArray)
				secondRunArray.append(columnList)
				continue
			else:
				if len(masterColumnList) == 0:
					masterColumnList = splitArray[1].strip()
				elif masterColumnList != splitArray[1].strip():
					print("Issue with " + line + "columns don't match. Ignoring and continuing")
					continue
				else:
					masterColumnArray = columnList
			districtDictionary = {}
			districtDictionary['districtName'] = linesArray[0]
			districtDictionary['confirmed'] = int(linesArray[2])
			districtDictionary['recovered'] = int(linesArray[4])
			districtDictionary['deceased'] = int(linesArray[6])
			districtArray.append(districtDictionary)

#Second run to correct possible misses with -999
	correctionIndex = ""
	for index, data in enumerate(secondRunArray):
		correctionIndex = ""
		if index % 2 == 1:
			rowValues = secondRunArray[index - 1]
			for colIndex, colValue in enumerate(data):
				if colValue.strip() != masterColumnArray[colIndex].strip():
					correctionIndex += "," + str(colIndex) if len(correctionIndex) != 0 else str(colIndex) 
					rowValues.insert(colIndex, -999)
					data.insert(colIndex, masterColumnArray[colIndex].strip())

			if len(rowValues) != 8 or len(data) != 8:
				print("Issue with data: {} ".format(rowValues))
				continue

			districtDictionary = {}
			districtDictionary['districtName'] = rowValues[0]
			districtDictionary['confirmed'] = int(rowValues[2])
			districtDictionary['recovered'] = int(rowValues[4])
			districtDictionary['deceased'] = int(rowValues[6])
			districtArray.append(districtDictionary)
			print("Tried a correction for: {} on columns: {}".format(rowValues, correctionIndex))
					


	deltaCalculator.getStateDataFromSite("Uttar Pradesh", districtArray, option)

def BRGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	with open("bihar.txt", "r") as upFile:
		for line in upFile:
			linesArray = line.split('|')[0].split(',')
			districtDictionary = {}
			districtDictionary['districtName'] = linesArray[0]
			districtDictionary['confirmed'] = int(linesArray[1])
			districtDictionary['recovered'] = int(linesArray[2])
			districtDictionary['deceased'] = int(linesArray[3])
			districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Bihar", districtArray, option)

def PBGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	with open("pb.txt", "r") as upFile:
		for line in upFile:
			linesArray = line.split(',')[0].split(',')
			districtDictionary = {}
			districtDictionary['districtName'] = linesArray[0]
			districtDictionary['confirmed'] = int(linesArray[1])
			districtDictionary['recovered'] = int(linesArray[3])
			districtDictionary['deceased'] = int(linesArray[4])
			districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Punjab", districtArray, option)
			
def TNGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	with open("tn.txt", "r") as upFile:
		for line in upFile:
			linesArray = line.split(',')
			districtDictionary = {}
			districtDictionary['districtName'] = linesArray[0]
			districtDictionary['confirmed'] = int(linesArray[1])
			districtDictionary['recovered'] = int(linesArray[2])
			districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
			districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Tamil Nadu", districtArray, option)


def NLGetData():
	print("NL has no proper table yet")
#os.system("curl -sk https://covid19.nagaland.gov.in > nl.html")
#	soup = BeautifulSoup(open("nl.html"), 'html5lib')
#	table = soup.find_all("script")[21].get_text()
#	print(table)

def ASGetData():
	response = requests.request("GET", metaDictionary['Assam'].url)
	soup = BeautifulSoup(response.content, 'html5lib')
	table = soup.find("tbody").find_all("tr")

	districtArray = []
	for index, row in enumerate(table):
		dataPoints = row.find_all("td")
    	
		districtDictionary = {}
		districtDictionary['districtName'] = dataPoints[0].get_text().strip()
		districtDictionary['confirmed'] = int(dataPoints[1].get_text().strip())
		districtDictionary['recovered'] = int(dataPoints[3].get_text().strip())
		districtDictionary['deceased'] = int(dataPoints[4].get_text().strip())
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Assam", districtArray, option)

def TRGetData():
	response = requests.request("GET", metaDictionary['Tripura'].url)
	soup = BeautifulSoup(response.content, 'html5lib')
	table = soup.find("tbody").find_all("tr")

	districtArray = []
	for index, row in enumerate(table):
		dataPoints = row.find_all("td")
    	
		districtDictionary = {}
		districtDictionary['districtName'] = dataPoints[1].get_text().strip()
		districtDictionary['confirmed'] = int(dataPoints[8].get_text().strip())
		districtDictionary['recovered'] = int(dataPoints[10].get_text().strip())
		districtDictionary['deceased'] = int(dataPoints[12].get_text().strip())
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Tripura", districtArray, option)

def PYGetData():
	response = requests.request("GET", metaDictionary['Puducherry'].url)
	soup = BeautifulSoup(response.content, 'html5lib')
	table = soup.find_all("tbody")[1].find_all("tr")

	districtArray = []
	for index, row in enumerate(table):
		dataPoints = row.find_all("td")
    	
		districtDictionary = {}
		districtDictionary['districtName'] = dataPoints[0].get_text().strip()
		districtDictionary['confirmed'] = int(dataPoints[1].get_text().strip())
		districtDictionary['recovered'] = int(dataPoints[2].get_text().strip())
		districtDictionary['deceased'] = -999
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Puducherry", districtArray, option)

def CHGetData():
	response = requests.request("GET", metaDictionary['Chandigarh'].url)
	soup = BeautifulSoup(response.content, 'html5lib')
	divs = soup.find("div", {"class": "col-lg-8 col-md-9 form-group pt-10"}).find_all("div", {"class": "col-md-3"})

	districtDictionary = {}
	districtArray = []
	districtDictionary['districtName'] = 'Chandigarh'
	
	for index, row in enumerate(divs):

		if index > 2:
			continue

		dataPoints = row.find("div", {"class": "card-body"}).get_text()

		if index == 0:
			districtDictionary['confirmed'] = int(dataPoints)
		if index == 1:
			districtDictionary['recovered'] = int(dataPoints)
		if index == 2:
			districtDictionary['deceased'] = int(dataPoints)

	districtArray.append(districtDictionary)
	deltaCalculator.getStateDataFromSite("Chandigarh", districtArray, option)


def KLGetData():
	response = requests.request("GET", metaDictionary['Kerala'].url)
	soup = BeautifulSoup(response.content, 'html5lib')
	table = soup.find_all("script")

	klData = open("kl.txt", "w")
	klData.writelines(table[len(table) - 1].get_text())
	klData.close()
	districtList = ""

	with open("kl.txt", "r") as klFile:
		for line in klFile:
			if "labels:" in line:
				print(line)
				distrctList = re.sub("labels: ", "", line)
				print(line)
			if "data:" in line: 
				print(line)

def LAGetData():
	response = requests.request("GET", metaDictionary['Ladakh'].url)
	soup = BeautifulSoup(response.content, 'html5lib')
	table = soup.find("table", id = "tableCovidData2").find_all("tr")

	districtArray = []
	districtDictionary = {}
	confirmed = table[9].find_all("td")[1]
	discharged = table[11].find_all("td")[1]
	confirmedArray = dischargedArray = []
	confirmedArray = re.sub(':', '', re.sub(' +', ' ', re.sub("\n", " ", confirmed.get_text().strip()))).split(' ')
	dischargedArray = re.sub(':', '', re.sub(' +', ' ', re.sub("\n", " ", discharged.get_text().strip()))).split(' ')

	districtDictionary['districtName'] = confirmedArray[0]
	districtDictionary['confirmed'] = int(confirmedArray[1])
	districtDictionary['recovered'] = int(dischargedArray[1])
	districtDictionary['deceased'] = -999
	districtArray.append(districtDictionary)

	districtDictionary = {}
	districtDictionary['districtName'] = confirmedArray[2]
	districtDictionary['confirmed'] = int(confirmedArray[3])
	districtDictionary['recovered'] = int(dischargedArray[3])
	districtDictionary['deceased'] = -999
	districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Ladakh", districtArray, option)
    	

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

#!/usr/bin/python3
import csv
import camelot
from bs4 import BeautifulSoup
import html5lib
from deltaCalculator import DeltaCalculator
import requests
import pdftotext
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
typeOfAutomation = "pdf"


class AutomationMeta:
	def __init__(self, stateName, stateCode, url):
		self.stateName = stateName
		self.stateCode = stateCode
		self.url = url

def fetchData(stateName):
	if stateName == "All States":
		for key, metaObject in metaDictionary.items():
			if len(metaObject.url.strip()) > 0:
				logging.info("Calling delta calculator for: " + metaObject.stateCode)
				eval(metaObject.stateCode + "GetData()")
				print("Dashboard url: " + metaObject.url)
	else:
		try:
			logging.info("Calling delta calculator for: " + metaDictionary[stateName].stateCode)
			eval(metaDictionary[stateName].stateCode + "GetData()")
			print("Dashboard url: " + metaDictionary[stateName].url)
		except KeyError:
			print("No entry found for state {} in automation.meta file".format(stateName))

def loadMetaData():
	with open("automation.meta", "r") as metaFile:
		for line in metaFile:
			if line.startswith('#'):
				continue
			lineArray = line.strip().split(',') 
			metaObject = AutomationMeta(lineArray[0].strip(), lineArray[1].strip(), lineArray[2].strip())
			metaDictionary[lineArray[0].strip()] = metaObject
	metaFile.close()

def APGetData():
	if typeOfAutomation == "ocr":
		APGetDataByOCR()
	else:
		APGetDataByUrl()

def APGetDataByOCR():
	districtArray = []
	with open(".tmp/ap.txt", "r") as upFile:
		for line in upFile:
			if 'Total' in line:
				continue

			linesArray = line.split('|')[0].split(',')
			if len(linesArray) != 6:
				print("Issue with {}".format(linesArray))
				continue

			districtDictionary = {}
			districtName = linesArray[0].strip()
			districtDictionary['districtName'] = linesArray[0].strip()
			districtDictionary['confirmed'] = int(linesArray[2])
			districtDictionary['recovered'] = int(linesArray[4])
			districtDictionary['deceased'] = int(linesArray[5]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
			districtArray.append(districtDictionary)
	upFile.close()

	deltaCalculator.getStateDataFromSite("Andhra Pradesh", districtArray, option)

def APGetDataByUrl():
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
	if typeOfAutomation == "ocr" or typeOfAutomation == "pdf":
		print("RJ Getdata using url is deprecated")
		return
	response = requests.request("GET", metaDictionary['Rajasthan'].url)
	soup = BeautifulSoup(response.content, 'html.parser')
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

	print(districtArray)
	deltaCalculator.getStateDataFromSite("Rajasthan", districtArray, option)


def GJGetData():
	response = requests.request("GET", metaDictionary['Gujarat'].url)
	soup = BeautifulSoup(response.content, 'html.parser')
	table = soup.find("div", {"class": "table-responsive"}).find_all("tr")
	
	districtArray = []
	for index, row in enumerate(table):
		if index == len(table) - 1:
			continue
    	
		dataPoints = row.find_all("td")
		if(len(dataPoints) != 6):
			continue

		districtDictionary = {}
		districtDictionary['districtName'] = dataPoints[0].get_text()
		districtDictionary['confirmed'] = int(dataPoints[1].get_text().strip())
		districtDictionary['recovered'] = int(dataPoints[3].get_text().strip())
		districtDictionary['deceased'] = int(dataPoints[5].get_text().strip())
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Gujarat", districtArray, option)


def TSGetData():
	response = requests.request("GET", metaDictionary['Telangana'].url)
	#response returns an invalid html and html.parser is not able to parse it properly. so, using html5lib to parse.
	soup = BeautifulSoup(response.content, 'html5lib')
	districtArray = []
	for tr in soup.tbody.find_all("tr", class_=None):
		data = tr.find_all('td')
		districtDictionary = {}
		districtDictionary['districtName'] = tr.find('th').get_text(strip=True)
		districtDictionary['confirmed'] = int(data[0].get_text(strip=True))
		districtDictionary['recovered'] = int(data[1].get_text(strip=True))
		districtDictionary['deceased'] = int(data[2].get_text(strip=True))
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Telangana", districtArray, option)


def UPGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	masterColumnArray = []
	splitArray = []
	try:
		with open(".tmp/up.txt", "r") as upFile:
			for line in upFile:
				splitArray = re.sub('\n', '', line.strip()).split('|')
				linesArray = splitArray[0].split(',')

				if len(linesArray) != 7:
					print("Issue with {}".format(linesArray))
					continue

				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0]
				districtDictionary['confirmed'] = int(linesArray[3]) + int(linesArray[5]) + int(linesArray[6])
				districtDictionary['recovered'] = int(linesArray[3])
				districtDictionary['deceased'] = int(linesArray[5])
				districtArray.append(districtDictionary)
		upFile.close()

		deltaCalculator.getStateDataFromSite("Uttar Pradesh", districtArray, option)
	except FileNotFoundError:
		print("up.txt missing. Generate through pdf or ocr and rerun.")

def BRGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	try:
		with open(".tmp/br.txt", "r") as upFile:
			for line in upFile:
				linesArray = line.split('|')[0].split(',')
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0]
				districtDictionary['confirmed'] = int(linesArray[1])
				districtDictionary['recovered'] = int(linesArray[2])
				districtDictionary['deceased'] = int(linesArray[3])
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("Bihar", districtArray, option)
	except FileNotFoundError:
		print("br.txt missing. Generate through pdf or ocr and rerun.")

def JHGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	try:
		with open(".tmp/jh.txt", "r") as upFile:
			for line in upFile:
				linesArray = line.split('|')[0].split(',')
				if len(linesArray) != 9:
					print(linesArray)
					continue;
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0].strip()
				districtDictionary['confirmed'] = int(linesArray[4]) + int(linesArray[5])
				districtDictionary['recovered'] = -999
				districtDictionary['deceased'] = -999
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("Jharkhand", districtArray, option)
	except FileNotFoundError:
		print("jh.txt missing. Generate through pdf or ocr and rerun.")

def RJGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	skipValues = False
	try:
		with open(".tmp/rj.txt", "r") as upFile:
			for line in upFile:
				if 'Other' in line:
					skipValues = True
					continue
				if skipValues == True:
					continue

				linesArray = line.split('|')[0].split(',')
				
				print(linesArray)
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0].strip().title()
				districtDictionary['confirmed'] = int(linesArray[3])
				districtDictionary['recovered'] = int(linesArray[7])
				districtDictionary['deceased'] = int(linesArray[5])
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("Rajasthan", districtArray, option)
	except FileNotFoundError:
		print("rj.txt missing. Generate through pdf or ocr and rerun.")

def MPGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	try:
		with open(".tmp/mp.txt", "r") as upFile:
			isIgnoreFlagSet = False
			for line in upFile:
				linesArray = line.split('|')[0].split(',')
				if 'Total' in line or isIgnoreFlagSet == True:
					isIgnoreFlagSet = True
					print("Ignoring {} ".format(line))
				if len(linesArray) != 8:
					print("Ignoring due to invalid length: {}".format(linesArray))
					continue
				districtDictionary = {}
				try:
					if is_number(linesArray[0].strip()):
						print("Ignoring: {}".format(linesArray))
						continue

					districtDictionary['districtName'] = linesArray[0].strip().title()
					districtDictionary['confirmed'] = int(linesArray[2])
					districtDictionary['recovered'] = int(linesArray[6])
					districtDictionary['deceased'] = int(linesArray[4])
					districtArray.append(districtDictionary)
				except ValueError:
					print("Ignoring: {}".format(linesArray))
					continue

		upFile.close()
		deltaCalculator.getStateDataFromSite("Madhya Pradesh", districtArray, option)
	except FileNotFoundError:
		print("rj.txt missing. Generate through pdf or ocr and rerun.")

def JKGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	try:
		with open(".tmp/jk.txt", "r") as upFile:
			isIgnoreFlagSet = False
			for line in upFile:
				linesArray = line.split('|')[0].split(',')
				if len(linesArray) != 11:
					print("Ignoring due to invalid length: {}".format(linesArray))
					continue
				districtDictionary = {}
				try:
					if is_number(linesArray[0].strip()):
						print("Ignoring: {}".format(linesArray))
						continue

					districtDictionary['districtName'] = linesArray[0].strip().title()
					districtDictionary['confirmed'] = int(linesArray[6])
					districtDictionary['recovered'] = int(linesArray[9])
					districtDictionary['deceased'] = int(linesArray[10])
					districtArray.append(districtDictionary)
				except ValueError:
					print("Ignoring: {}".format(linesArray))
					continue

		upFile.close()
		deltaCalculator.getStateDataFromSite("Jammu and Kashmir", districtArray, option)
	except FileNotFoundError:
		print("rj.txt missing. Generate through pdf or ocr and rerun.")

def WBGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	readFileFromURLV2(metaDictionary['West Bengal'].url, "West Bengal", "Alipurduar", "TOTAL")
	try:
		with open(".tmp/WB.csv", "r") as upFile:
			for line in upFile:
				linesArray = line.split(',')
				if len(linesArray) != 7:
					print("Issue with {}".format(linesArray))
					continue
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[1].strip()
				districtDictionary['confirmed'] = int(linesArray[2])
				districtDictionary['recovered'] = int(linesArray[3])
				districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("West Bengal", districtArray, option)
	except FileNotFoundError:
		print("wb.txt missing. Generate through pdf or ocr and rerun.")

def PBGetDataThroughPdf():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	readFileFromURL(metaDictionary['Punjab'].url, "Punjab", "Amritsar", "Total")
	try:
		with open(".tmp/PB.txt", "r") as upFile:
			for line in upFile:
				linesArray = line.split(',')
				if len(linesArray) != 5:
					print("Issue with {}".format(linesArray))
					continue
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0].strip()
				districtDictionary['confirmed'] = int(linesArray[1])
				districtDictionary['recovered'] = int(linesArray[3])
				districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("Punjab", districtArray, option)
	except FileNotFoundError:
		print("pb.txt missing. Generate through pdf or ocr and rerun.")

def PBGetData():
	if typeOfAutomation == "pdf":
		PBGetDataThroughPdf()
	else:
		PBGetDataThroughOcr()

def PBGetDataThroughOcr():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	secondRunArray = []
	masterColumnList = ""
	masterColumnArray = []
	splitArray = []
	try:
		with open(".tmp/pb.txt", "r") as upFile:
			for line in upFile:
				splitArray = re.sub('\n', '', line.strip()).split('|')
				linesArray = splitArray[0].split(',')

				if len(linesArray) != 5:
					print("Issue with {}".format(linesArray))
					continue
				if linesArray[0].strip() == "Total":
					continue
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0].strip()
				districtDictionary['confirmed'] = int(linesArray[1])
				districtDictionary['recovered'] = int(linesArray[3])
				districtDictionary['deceased'] = int(linesArray[4])
				districtArray.append(districtDictionary)

		upFile.close()

		deltaCalculator.getStateDataFromSite("Punjab", districtArray, option)
	except FileNotFoundError:
		print("pb.txt missing. Generate through pdf or ocr and rerun.")

def KAGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	readFileFromURL('', "Karnataka", "Bengaluru Urban", "Total")
	try:
		with open(".tmp/ka.txt", "r") as upFile:
			for line in upFile:
				linesArray = line.split(',')
				if len(linesArray) != 8:
					print("Issue with {}".format(linesArray))
					continue
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0].strip()
				districtDictionary['confirmed'] = int(linesArray[2])
				districtDictionary['recovered'] = int(linesArray[4])
				districtDictionary['deceased'] = int(linesArray[6]) if len(re.sub('\n', '', linesArray[7])) != 0 else 0
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("Karnataka", districtArray, option)
	except FileNotFoundError:
		print("ka.txt missing. Generate through pdf or ocr and rerun.")

def HRGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	if typeOfAutomation == "pdf":
		readFileFromURL(metaDictionary['Haryana'].url, "Haryana", "Gurugram", "Italian")
	try:
		with open(".tmp/hr.txt", "r") as upFile:
			for line in upFile:
				linesArray = line.split(',')
				if len(linesArray) != 4:
					print("Issue with {}".format(linesArray))
					continue
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0].strip()
				districtDictionary['confirmed'] = int(linesArray[1])
				districtDictionary['recovered'] = int(linesArray[2])
				districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("Haryana", districtArray, option)
	except FileNotFoundError:
		print("hr.txt missing. Generate through pdf or ocr and rerun.")
			
def TNGetData():
	linesArray = []
	districtDictionary = {}
	districtArray = []
	convertTnPDFToCSV()
	try:
		with open(".tmp/tn.csv", "r") as upFile:
			for line in upFile:
				linesArray = line.split(',')
				if len(linesArray) != 4:
					print("Issue with {}".format(linesArray))
					continue
				linesArray[3] = linesArray[3].replace('$', '')
				districtDictionary = {}
				districtDictionary['districtName'] = linesArray[0].strip()
				districtDictionary['confirmed'] = int(linesArray[1])
				districtDictionary['recovered'] = int(linesArray[2])
				districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
				districtArray.append(districtDictionary)

		upFile.close()
		deltaCalculator.getStateDataFromSite("Tamil Nadu", districtArray, option)
	except FileNotFoundError:
		print("tn.txt missing. Generate through pdf or ocr and rerun.")

def NLGetData():
	print("NL has no proper table yet")
#os.system("curl -sk https://covid19.nagaland.gov.in > nl.html")
#	soup = BeautifulSoup(open("nl.html"), 'html.parser')
#	table = soup.find_all("script")[21].get_text()
#	print(table)

def ASGetData():
	response = requests.request("GET", metaDictionary['Assam'].url)
	soup = BeautifulSoup(response.content, 'html.parser')
	table = soup.find("tbody").find_all("tr")

	districtArray = []
	for index, row in enumerate(table):
		dataPoints = row.find_all("td")
    	
		districtDictionary = {}
		districtDictionary['districtName'] = dataPoints[0].get_text().strip() 
		districtDictionary['confirmed'] = int(dataPoints[1].get_text().strip()) if '-' not in dataPoints[1].get_text().strip() else 0
		districtDictionary['recovered'] = int(dataPoints[3].get_text().strip()) if '-' not in dataPoints[3].get_text().strip() else 0
		districtDictionary['deceased'] = int(dataPoints[4].get_text().strip()) if '-' not in dataPoints[4].get_text().strip() else 0
		districtArray.append(districtDictionary)

	deltaCalculator.getStateDataFromSite("Assam", districtArray, option)

def TRGetData():
	response = requests.request("GET", metaDictionary['Tripura'].url)
	soup = BeautifulSoup(response.content, 'html.parser')
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
	soup = BeautifulSoup(response.content, 'html.parser')
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
	soup = BeautifulSoup(response.content, 'html.parser')
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
	response = requests.request("GET", 'https://dashboard.kerala.gov.in/index.php')
	sessionId = (response.headers['Set-Cookie']).split(';')[0].split('=')[1]

	cookies = {
		'_ga': 'GA1.3.594771251.1592531338',
		'_gid': 'GA1.3.674470591.1592531338',
		'PHPSESSID': sessionId,
		'_gat_gtag_UA_162482846_1': '1',
	}

	headers = {
		'Connection': 'keep-alive',
		'Accept': 'application/json, text/javascript, */*; q=0.01',
		'X-Requested-With': 'XMLHttpRequest',
		'Sec-Fetch-Site': 'same-origin',
		'Sec-Fetch-Mode': 'cors',
		'Sec-Fetch-Dest': 'empty',
		'Referer': 'https://dashboard.kerala.gov.in/index.php',
		'Accept-Language': 'en-US,en;q=0.9',
	}

	stateDashboard = requests.get(metaDictionary['Kerala'].url, headers=headers, cookies=cookies).json()
	districtArray = []
	for districtDetails in stateDashboard['features']:
		districtDictionary = {}
		districtDictionary['districtName'] = districtDetails['properties']['District']
		districtDictionary['confirmed'] = districtDetails['properties']['covid_stat']
		districtDictionary['recovered'] = districtDetails['properties']['covid_statcured']
		districtDictionary['deceased'] = districtDetails['properties']['covid_statdeath']
		districtArray.append(districtDictionary)
	deltaCalculator.getStateDataFromSite("Kerala", districtArray, option)


def MLGetData():
	stateDashboard = requests.get(metaDictionary['Meghalaya'].url).json()
	districtArray = []
	for districtDetails in stateDashboard['features']:
		districtDictionary = {}
		districtDictionary['districtName'] = districtDetails['attributes']['Name']
		districtDictionary['confirmed'] = districtDetails['attributes']['Positive']
		districtDictionary['recovered'] = districtDetails['attributes']['Recovered']
		districtDictionary['deceased'] = districtDetails['attributes']['Deceasesd']
		districtArray.append(districtDictionary)
	deltaCalculator.getStateDataFromSite("Meghalaya", districtArray, option)


def LAGetData():
	response = requests.request("GET", metaDictionary['Ladakh'].url)
	soup = BeautifulSoup(response.content, 'html.parser')
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
    	
def PBFormatLine(line):
	line = re.sub(' +', ',', re.sub("^ +", '', line))
	linesArray = line.split(',')

	outputString = ""
	for index, data in enumerate(linesArray):
		if index == 0:
			continue
		if is_number(data) == False:
			outputString = outputString + " " + data if len(outputString) != 0 else data
		else:
			outputString += "," + str(data)
	return outputString

def KAFormatLine(line):
	line = re.sub(' +', ',', re.sub('^ +', '', line))
	linesArray = line.split(',')

	outputString = ""
	for index, data in enumerate(linesArray):
		if index == 0:
			continue
		if is_number(data) == False:
			outputString = outputString + " " + data if len(outputString) != 0 else data
		else:
			outputString += "," + str(data)
	return outputString

def HRFormatLine(line):
	line = re.sub(' +', ',', re.sub('^ +', '', line))

	linesArray = line.split(',')

	if len(linesArray) > 1 and linesArray[1] == "Charkhi":
		linesArray.remove("Dadri")
		linesArray[1] = "Charkhi Dadri"

	if len(linesArray) != 11:
		print("Ignoring: {}".format(linesArray))
		return "\n"
	
	recovery = 0
	if '[' in linesArray[4]:
		recovery = linesArray[4].split('[')[0]
	else:
		recovery = linesArray[4]

	deaths = 0
	if '[' in linesArray[7]:
		deaths = linesArray[7].split('[')[0]
	else:
		deaths = linesArray[7]

	outputString = linesArray[1] + "," + linesArray[3] + "," + str(recovery) + "," + str(deaths) + "\n"
	return outputString


def WBFormatLine(row):
	row[2] = re.sub(',', '', re.sub('\+.*', '', row[2]))
	row[3] = re.sub(',', '', re.sub('\+.*', '', row[3]))
	row[4] = re.sub(',', '', re.sub('\+.*', '', row[4]))
	row[5] = re.sub(',', '', re.sub('\+.*', '', row[5]))
	line = ",".join(row) + "\n"
	return line


def readFileFromURLV2(url, stateName, startKey, endKey):
	stateFileName = metaDictionary[stateName].stateCode 
	pid = input("Enter district page:")
	tables = camelot.read_pdf(".tmp/" + stateFileName + ".pdf", strip_text = '\n', pages = pid)
	for index, table in enumerate(tables):
		tables[index].to_csv('.tmp/' + stateFileName + str(index) + '.pdf.txt')

	stateOutputFile = open('.tmp/' + stateFileName + '.csv', 'w')
	csvWriter = csv.writer(stateOutputFile)
	arrayToWrite = []

	startedReadingDistricts = False
	for index, table in enumerate(tables):
		with open('.tmp/' + stateFileName + str(index) + '.pdf.txt', newline='') as stateCSVFile:
			rowReader = csv.reader(stateCSVFile, delimiter=',', quotechar='"')
			for row in rowReader:
				line = "|".join(row)
				if startKey in line:
					startedReadingDistricts = True
				if endKey in line:
					startedReadingDistricts = False
					continue
				if startedReadingDistricts == False:
					continue

				line = eval(stateFileName + "FormatLine")(row)
				print(line, file = stateOutputFile)

	stateOutputFile.close()
				

def readFileFromURL(url, stateName, startKey, endKey):
	stateFileName = metaDictionary[stateName].stateCode 
	if len(url) > 0:
		r = requests.get(url, allow_redirects=True)
		open(".tmp/" + stateFileName + ".pdf", 'wb').write(r.content)

	with open(".tmp/" + stateFileName + ".pdf", "rb") as f:
		pdf = pdftotext.PDF(f)

	fileToWrite = open(".tmp/" + stateFileName + ".pdf.txt", "w")
	pid = input("Enter district page:")
	print(pdf[int(pid)], file = fileToWrite)
	fileToWrite.close()

	fileToWrite = open(".tmp/" + stateFileName + '.pdf.txt', 'r') 
	lines = fileToWrite.readlines() 
	stateOutputFileName = open(".tmp/" + stateFileName + '.txt', 'w') 

	startedReadingDistricts = False
	outputLines = []
	for line in lines:
		if startKey in line:
			startedReadingDistricts = True
		if endKey in line:
			startedReadingDistricts = False
			continue

		if startedReadingDistricts == False:
			continue
		print(eval(stateFileName + "FormatLine")(line), file = stateOutputFileName, end = " ")

	stateOutputFileName.close()
	fileToWrite.close()


def convertTnPDFToCSV():
	try:
		with open(".tmp/" + "tn.pdf", "rb") as f:
				pdf = pdftotext.PDF(f)
	except FileNotFoundError:
		print("Make sure tn.pdf is present in the current folder and rerun the script! Arigatou gozaimasu.")
		return

	tables = camelot.read_pdf('.tmp/tn.pdf',strip_text='\n', pages="6", split_text = True)
	tables[0].to_csv('.tmp/tn.pdf.txt')

	tnFile = open(".tmp/" + 'tn.pdf.txt', 'r') 
	lines = tnFile.readlines() 
	tnOutputFile = open(".tmp/" + 'tn.csv', 'w') 

	startedReadingDistricts = False
	airportRun = 1
	airportConfirmedCount = 0
	airportRecoveredCount = 0
	airportDeceasedCount = 0
	with open('.tmp/tn.pdf.txt', newline='') as csvfile:
		rowReader = csv.reader(csvfile, delimiter=',', quotechar='"')
		line = ""
		for row in rowReader:
			line = '|'.join(row)
	
			if 'Ariyalur' in line:
				startedReadingDistricts = True
			if 'Total' in line:
				startedReadingDistricts = False

			if startedReadingDistricts == False:
				continue

			line = line.replace('"', '').replace('*', '').replace('#', '').replace(',', '').replace('$', '')
			linesArray = line.split('|')

			if len(linesArray) < 6:
				print("Ignoring line: {} due to less columns".format(line))
				continue

			if 'Airport' in line:
				airportConfirmedCount += int(linesArray[2])
				airportRecoveredCount += int(linesArray[3])
				airportDeceasedCount += int(linesArray[5])
				if airportRun == 1:
					airportRun += 1
					continue
				else:
					print("{}, {}, {}, {}\n".format('Airport Quarantine', airportConfirmedCount, airportRecoveredCount, airportDeceasedCount), file = tnOutputFile)
					continue
			if 'Railway' in line:
				print("{}, {}, {}, {}".format('Railway Quarantine', linesArray[2], linesArray[3], linesArray[5]), file = tnOutputFile)
				continue

			print("{}, {}, {}, {}".format(linesArray[1], linesArray[2], linesArray[3], linesArray[5]), file = tnOutputFile)

	tnOutputFile.close()

def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

def main():

	loadMetaData()
	stateName = ""
	global option 
	global typeOfAutomation

	if len(sys.argv) not in [1, 2, 3, 4]:
		print('Usage: ./automation "[StateName]" "[detailed/full]" "[ocr/pdf]"')
		return

	if len(sys.argv) == 2:
		stateName = sys.argv[1]

	if len(sys.argv) == 3:
		stateName = sys.argv[1]
		option = sys.argv[2]

	if len(sys.argv) == 4:
		stateName = sys.argv[1]
		option = sys.argv[2]
		typeOfAutomation = sys.argv[3]
	
	if not stateName:
		stateName = "All States"
	fetchData(stateName)

if __name__ == '__main__':
	main()

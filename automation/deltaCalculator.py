import requests
import json
import logging
import re
import sys
logging.basicConfig(filename='deltaCalculator.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class DeltaCalculator:
	def __init__(self, stateName = ''):
		self.covidDashboardData = requests.request("get", "https://api.covid19india.org/state_district_wise.json").json()
		self.nameMapping = {}
		self.loadMetaData()

	def loadMetaData(self):
		with open("nameMapping.meta", "r") as metaFile:
			lineArray = []
			for line in metaFile:
				lineArray = line.split(',')
				districtMapping = {}

				currentDictionary = {}
				if lineArray[0] not in self.nameMapping:
					self.nameMapping[lineArray[0]] = {}

				currentDictionary = self.nameMapping[lineArray[0]]
				currentDictionary[lineArray[1].strip()] = re.sub('\n', '', lineArray[2].strip())
				self.nameMapping[lineArray[0]] = currentDictionary

	
	def getStateDataFromSite(self, stateName, stateDataFromStateDashboard, options):
		logging.info(stateDataFromStateDashboard)
		stateData = self.covidDashboardData[stateName]['districtData']
		print('*' * 20 + stateName + '*' * 20)
		try:
			nameMapping = self.nameMapping[stateName]
		except KeyError:
			nameMapping = {}

		confirmedDeltaArray = []
		recoveredDeltaArray = []
		deceasedDeltaArray = []
		districts = []

		for districtDetails in stateDataFromStateDashboard:
			districtName = nameMapping[districtDetails['districtName']] if districtDetails['districtName'] in nameMapping else districtDetails['districtName']
			outputString = ""

			confirmedDelta = districtDetails['confirmed'] - stateData[districtName]['confirmed'] if districtDetails['confirmed'] != -999 else "NA"
			recoveredDelta = districtDetails['recovered'] - stateData[districtName]['recovered'] if districtDetails['recovered'] != -999 else "NA"
			deceasedDelta = districtDetails['deceased'] - stateData[districtName]['deceased'] if districtDetails['deceased'] != -999 else "NA"

			if not options:
				outputString = districtName + ", " + str(confirmedDelta) + ", " + str(recoveredDelta) + ", " + str(deceasedDelta) 
				print(outputString)
			if options == "detailed":
				districts.append(districtName)
				if confirmedDelta != 0 and confirmedDelta != "NA":
					confirmedDeltaArray.append(confirmedDelta)
				if recoveredDelta != 0 and recoveredDelta != "NA":
					recoveredDeltaArray.append(recoveredDelta)
				if deceasedDelta != 0 and deceasedDelta != "NA":
					deceasedDeltaArray.append(deceasedDelta)

		if options == "detailed":
			self.printDistricts(self.printDeltas(confirmedDeltaArray, "Confirmed"), districts)
			self.printDistricts(self.printDeltas(recoveredDeltaArray, "Recovered"), districts)
			self.printDistricts(self.printDeltas(deceasedDeltaArray, "Deceased"), districts)

	def printDeltas(self, deltaArray, category):
		print('-' * 20 + category + '-' * 20)
		printIndex = []
		for index, data in enumerate(deltaArray):
			print(data)
			printIndex.append(index)

		return printIndex

	def printDistricts(self, printIndex, districts):
		for data in printIndex:
			print(districts[data])

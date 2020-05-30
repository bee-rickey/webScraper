import requests
import json
import logging
import re
import sys

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

	
	def getStateDataFromSite(self, stateName, stateDataFromStateDashboard):
		stateData = self.covidDashboardData[stateName]['districtData']
		print('*' * 20 + stateName + '*' * 20)
		try:
			nameMapping = self.nameMapping[stateName]
		except KeyError:
			nameMapping = {}

		for districtDetails in stateDataFromStateDashboard:
			districtName = nameMapping[districtDetails['districtName']] if districtDetails['districtName'] in nameMapping else districtDetails['districtName']
			outputString = ""

			confirmedDelta = districtDetails['confirmed'] - stateData[districtName]['confirmed'] if districtDetails['confirmed'] != -999 else "NA"
			recoveredDelta = districtDetails['recovered'] - stateData[districtName]['recovered'] if districtDetails['recovered'] != -999 else "NA"
			deceasedDelta = districtDetails['deceased'] - stateData[districtName]['deceased'] if districtDetails['deceased'] != -999 else "NA"

			outputString = districtName + ", " + str(confirmedDelta) + ", " + str(recoveredDelta) + ", " + str(deceasedDelta) 
			print(outputString)


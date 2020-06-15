import requests
import json
import logging
import re
import sys
logging.basicConfig(filename='deltaCalculator.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

class DeltaCalculator:
	def __init__(self, lightLoad = False):
		if lightLoad == False:
			self.covidDashboardData = requests.request("get", "https://api.covid19india.org/state_district_wise.json").json()
		self.nameMapping = {}
		self.loadMetaData()

	def getNameMapping(self, stateName, districtName):
		mappedDistrict = ""
		try:
			nameMapping = self.nameMapping[stateName]
			mappedDistrict = nameMapping[districtName]
		except KeyError:
			mappedDistrict = districtName

		return mappedDistrict


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
		print("\n" + '*' * 20 + stateName + '*' * 20)
		try:
			nameMapping = self.nameMapping[stateName]
		except KeyError:
			nameMapping = {}

		confirmedDeltaArray = []
		recoveredDeltaArray = []
		deceasedDeltaArray = []
		districts = []
		stateTotalFromStateDashboard = {'confirmed': 0, 'recovered': 0, 'deceased': 0}
		siteTotalFromStateDashboard = {'confirmed': 0, 'recovered': 0, 'deceased': 0}

		for districtDetails in stateDataFromStateDashboard:
			try:
				districtName = nameMapping[districtDetails['districtName']] if districtDetails['districtName'] in nameMapping else districtDetails['districtName']
				outputString = ""

				stateTotalFromStateDashboard['confirmed'] += districtDetails['confirmed'] if districtDetails['confirmed'] != -999 else 0
				stateTotalFromStateDashboard['recovered'] += districtDetails['recovered'] if districtDetails['recovered'] != -999 else 0
				stateTotalFromStateDashboard['deceased'] += districtDetails['deceased'] if districtDetails['deceased'] != -999 else 0

				siteTotalFromStateDashboard['confirmed'] += stateData[districtName]['confirmed']
				siteTotalFromStateDashboard['recovered'] += stateData[districtName]['recovered']
				siteTotalFromStateDashboard['deceased'] += stateData[districtName]['deceased']

				confirmedDelta = districtDetails['confirmed'] - stateData[districtName]['confirmed'] if districtDetails['confirmed'] != -999 else "NA"
				recoveredDelta = districtDetails['recovered'] - stateData[districtName]['recovered'] if districtDetails['recovered'] != -999 else "NA"
				deceasedDelta = districtDetails['deceased'] - stateData[districtName]['deceased'] if districtDetails['deceased'] != -999 else "NA"
			except KeyError:
				print("ERROR: Failed to find key mapping for district: {}, state: {}".format(districtName, stateName))
				continue

			if not options:
				outputString = districtName + ", " + str(confirmedDelta) + ", " + str(recoveredDelta) + ", " + str(deceasedDelta) 
				print(outputString)
			if options == "detailed":
				districts.append(districtName)
				confirmedDeltaArray.append(confirmedDelta)
				recoveredDeltaArray.append(recoveredDelta)
				deceasedDeltaArray.append(deceasedDelta)

		stateConfirmedDelta = stateTotalFromStateDashboard['confirmed'] - siteTotalFromStateDashboard['confirmed'] 
		stateRecoveredDelta = stateTotalFromStateDashboard['recovered'] - siteTotalFromStateDashboard['recovered']
		stateDeceasedDelta = stateTotalFromStateDashboard['deceased'] - siteTotalFromStateDashboard['deceased']

		if options == "detailed":
				districts.append('Total')
				confirmedDeltaArray.append(stateConfirmedDelta)
				recoveredDeltaArray.append(stateRecoveredDelta)
				deceasedDeltaArray.append(stateDeceasedDelta)

				self.printDistricts(self.printDeltas(confirmedDeltaArray, "Confirmed"), districts)
				self.printDistricts(self.printDeltas(recoveredDeltaArray, "Recovered"), districts)
				self.printDistricts(self.printDeltas(deceasedDeltaArray, "Deceased"), districts)
		else:
			print("Total delta, {}, {}, {}".format(stateConfirmedDelta, stateRecoveredDelta, stateDeceasedDelta))

		print("StateTotal, {}, {}, {}".format(stateTotalFromStateDashboard['confirmed'], stateTotalFromStateDashboard['recovered'], stateTotalFromStateDashboard['deceased']))
		print("SiteTotal, {}, {}, {}".format(siteTotalFromStateDashboard['confirmed'], siteTotalFromStateDashboard['recovered'], siteTotalFromStateDashboard['deceased']))

	def printDeltas(self, deltaArray, category):
		print('-' * 20 + category + '-' * 20)
		printIndex = []
		for index, data in enumerate(deltaArray):
			if data != 0 and data != "NA":
				print(data)
				printIndex.append(index)

		return printIndex

	def printDistricts(self, printIndex, districts):
		for data in printIndex:
			print(districts[data])

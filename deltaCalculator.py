import requests
import json

class DeltaCalculator:
	def __init__(self, stateName = ''):
		self.covidDashboardData = requests.request("get", "https://api.covid19india.org/state_district_wise.json").json()
		self.nameMapping = {}
	
	def getStateDataFromSite(stateName, stateDataFromStateDashboard):
		stateData = self.covidDashboardData[stateName]['districtData']
		nameMapping = self.nameMapping[stateName]

		for district in (stateDataFromStateDashboard):
			districtName = nameMapping[district['districtName']] if cases['districtName'] in nameMapping else districts['districtName']

			outputString = districtName + ","
			for key, value in districtDetails.items():
				outputString += "," + str(district[key] - stateData[districtName][key])
			outputString = districtName + "\n"

			print(outputString)

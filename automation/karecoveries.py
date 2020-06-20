#!/usr/bin/python3
import requests
import csv
import camelot
import re
import datetime
from deltaCalculator import DeltaCalculator

deltaCalculator = DeltaCalculator(True)

def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

tables = camelot.read_pdf('.tmp/ka.pdf',strip_text='\n', pages="4")

kaOutputFile = open('karecoveries.csv', 'w') 
for index, table in enumerate(tables):
	tables[index].to_csv('.tmp/ka' + str(index) + '.csv')

for index, table in enumerate(tables):

	with open('.tmp/ka' + str(index) + '.csv', newline='') as kaFile:
		rowReader = csv.reader(kaFile, delimiter=',', quotechar='"')
		for row in rowReader:
			line = '|'.join(row)
			line = re.sub('^\|+', '', line)
			print(line)
			linesArray = line.split('|')
			if len(linesArray) < 3:
				print("Ignoring {} ".format(line))
				continue

			districtName = linesArray[1].split('(')[0].strip()
			districtName = deltaCalculator.getNameMapping('Karnataka', districtName)

			patientIds = re.sub('&', ',', re.sub(' +', '', linesArray[2]))
			patientIdArray = patientIds.split(',')

			print("{} -- {}".format(districtName, patientIdArray))

			for item in patientIdArray:
				if len(item) == 0 or is_number(item) or '(' in item:	
					continue
				if item == "\n":
					continue
				print("{},{},{},{},{},{},{},{},{},{}".format(item.replace('P-', 'KA-P').replace('\n', ''), datetime.date.today().strftime("%d/%m/%Y"), '', '','',districtName,'Karnataka', 'KA', 1, 'Recovered'), file = kaOutputFile)


		
		"""
		patientId = []

		for item in linesArray:
			if len(item) == 0 or is_number(item) or '(' in item:	
				continue
			patientId.append(item)
		for item in patientId:
			if item == "\n":
				continue
			print("{},{},{},{},{},{},{},{},{},{}".format(item.replace('P-', 'KA-P').replace('\n', ''), datetime.date.today().strftime("%d/%m/%Y"), '', '','',districtName,'Karnataka', 'KA', 1, 'Recovered'), file = kaOutputFile)
			"""

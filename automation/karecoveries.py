#!/usr/bin/python3
import requests
import pdftotext
import PyPDF2 as pypdf
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
	kaFile = open('.tmp/ka' + str(index) + '.csv', 'r') 
	lines = kaFile.readlines()

	for line in lines:
		line = re.sub(',+$', '', re.sub('^,+', '', line.replace('\"', '').replace('&', ' ')))
		if len(line.split(',')) < 3:
			continue
		districtName = line.split(',')[1].split('(')[0]
		districtName = deltaCalculator.getNameMapping('Karnataka', districtName.strip())
		linesArray = line.split(',')[2].split(' ')
		patientId = []

		for item in linesArray:
			if len(item) == 0 or is_number(item):	
				continue
			patientId.append(item)
		for item in patientId:
			if item == "\n":
				continue
			print("{},{},{},{},{},{},{},{},{},{}".format(item.replace('P-', 'KA-P').replace('\n', ''), datetime.date.today().strftime("%d/%m/%Y"), '', '','',districtName,'Karnataka', 'KA', 1, 'Recovered'), file = kaOutputFile)

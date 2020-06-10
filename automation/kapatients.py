import requests
import pdftotext
import PyPDF2 as pypdf
import camelot
import re
import datetime
import matplotlib.pyplot as plt
from deltaCalculator import DeltaCalculator

deltaCalculator = DeltaCalculator(True)
startPid = input("Enter start page number:")
endPid = input("Enter end page number:")
pages = ""

for i in range(int(startPid), int(endPid) + 1):
	pages = pages + "," + str(i) if len(pages) != 0 else str(i)
print(pages)

tables = camelot.read_pdf('ka.pdf',strip_text='\n', pages=pages, split_text = True)

for index, table in enumerate(tables):
	tables[index].to_csv('.tmp/ka' + str(index) + '.csv')

kaOutputFile = open('kafull.csv', 'w') 
for index, table in enumerate(tables):
	kaFile = open('.tmp/ka' + str(index) + '.csv', 'r') 
	lines = kaFile.readlines()

	for line in lines:
		line = line.replace('\"', '')
		linesArray = line.split(',')
		if len(linesArray[7]) == 0:
			continue

		gender = ""
		if linesArray[6].strip() == 'Female':
			gender = 'F'
		elif linesArray[6].strip() == 'Male':
			gender = 'M'
		else:
			gender = 'Non-Binary'

		districtName = ""
		districtName = deltaCalculator.getNameMapping('Karnataka', linesArray[7])
		print("{},{},{},{},{},{},{},{},{},{},{}".format(linesArray[4].replace('P-', 'KA-P'), datetime.date.today().strftime("%d/%m/%Y"), linesArray[5], gender, '', districtName, 'Karnataka', 'KA', 1, 'Hospitalized', linesArray[8]), file = kaOutputFile)
	kaFile.close()
kaOutputFile.close()

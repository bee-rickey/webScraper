#!/usr/bin/python3
import csv
import requests
import camelot
import re
import datetime
from deltaCalculator import DeltaCalculator

deltaCalculator = DeltaCalculator(True)
category = input("Enter c/r/d : ")

def readPDF():
	startPid = input("Enter start page number: ")
	endPid = input("Enter end page number: ")
	pages = ""
	for i in range(int(startPid), int(endPid) + 1):
		pages = pages + "," + str(i) if len(pages) != 0 else str(i)
	print(pages)

	tables = camelot.read_pdf('.tmp/ka.pdf',strip_text='\n', pages=pages, split_text = True)

	for index, table in enumerate(tables):
		tables[index].to_csv('.tmp/ka' + str(index) + '.csv')

	processTmpFiles(tables)


def processTmpFiles(tables):
	kaOutputFile = open('kaconfirmed.csv', 'w') 
	csvWriter = csv.writer(kaOutputFile, delimiter=',', quotechar='"')
	for index, table in enumerate(tables):
		kaFile = open('.tmp/ka' + str(index) + '.csv', 'r') 
		with open('.tmp/ka' + str(index) + '.csv', newline='') as kaFile:
			rowReader = csv.reader(kaFile, delimiter=',', quotechar='"')
			for row in rowReader:
				line = '|'.join(row)
				line = re.sub('\|$', '', re.sub('^\|+', '', line.replace('\"', '').replace(',,', ',')))
				linesArray = line.split('|')

				if category == "c":
					confirmedFileWriter(linesArray, csvWriter)

				if category == "r":
					recoveredFileWriter(linesArray, csvWriter)

				if category == "d":
					deceasedFileWriter(linesArray, csvWriter)

		kaFile.close()
	kaOutputFile.close()


def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False


def confirmedFileWriter(linesArray, csvWriter):
	if len(linesArray) != 8 or len(linesArray[5]) == 0:
		print("Ignoring {}".format(linesArray))
		return ""

	gender = ""
	if linesArray[4].strip() == 'Female':
		gender = 'F'
	elif linesArray[4].strip() == 'Male':
		gender = 'M'
	else:
		gender = 'Non-Binary'

	districtName = ""
	districtName = deltaCalculator.getNameMapping('Karnataka', linesArray[5])
	csvWriter.writerow([linesArray[2].replace('P-', 'KA-P'), datetime.date.today().strftime("%d/%m/%Y"), linesArray[3], gender, '', districtName, 'Karnataka', 'KA', 1, 'Hospitalized','', linesArray[6]])


def recoveredFileWriter(linesArray, csvWriter):
	if len(linesArray) < 3:
		print("Ignoring {} ".format(linesArray))
		return ""

	districtName = linesArray[1].split('(')[0].strip()
	districtName = deltaCalculator.getNameMapping('Karnataka', districtName)

	patientIds = re.sub('\.', '', re.sub('&', ',', re.sub(' +', ',', linesArray[3])))
	patientIdArray = patientIds.split(',')
	print(patientIdArray)
	print("{} ---> {}".format(districtName, patientIdArray))

	for item in patientIdArray:
		if len(item) == 0: #or is_number(item) or '(' in item:	
			continue
		if item == "\n":
			continue
		csvWriter.writerow([item.replace('P-', 'KA-P').replace('\n', ''), datetime.date.today().strftime("%d/%m/%Y"), '', '','',districtName,'Karnataka', 'KA', 1, 'Recovered'])
	

def deceasedFileWriter(linesArray, csvWriter):
	if len(linesArray) < 10 or len(linesArray[1]) == 0:
		print("Ignoring {} ".format(linesArray))
		return ""

	districtName = linesArray[1].strip()
	districtName = deltaCalculator.getNameMapping('Karnataka', districtName)
	description = linesArray[5] + "; " + linesArray[6] + "; " + linesArray[7] + "; DOA: " + linesArray[8] + "; DOD " + linesArray[9]
	csvWriter.writerow(["KA-P" + str(linesArray[2]), datetime.date.today().strftime("%d/%m/%Y"), linesArray[3], linesArray[4], '', districtName, 'Karnataka', 'KA', 1, 'Deceased', '', description])


readPDF()

#!/usr/bin/python3
import sys
import csv
import requests
import camelot
import re
import datetime
from deltaCalculator import DeltaCalculator

deltaCalculator = DeltaCalculator(True)
category = "d"

def readPDF():
  """
  r = requests.get(sys.argv[1], allow_redirects=True)  
  print("URL: " + sys.argv[1])
  open(".tmp/ka.pdf", 'wb').write(r.content)
  """

  print(10*"-" + " Deceased details (IGNORE THE FIRST TWO LINES) " + 10*"-")
  if len(sys.argv) == 4:
    category = sys.argv[1]
    startPid = sys.argv[2]
    endPid = sys.argv[3]
  else:
    category = input("Enter c/r/d : ")
    startPid = input("Enter start page number: ")
    endPid = input("Enter end page number: ")

  pages = ""
  for i in range(int(startPid), int(endPid) + 1):
    pages = pages + "," + str(i) if len(pages) != 0 else str(i)
  print(f"Processing pages {pages}")

  tables = camelot.read_pdf('.tmp/KA.pdf',strip_text='\n', pages=pages, split_text = True)

  for index, table in enumerate(tables):
    tables[index].to_csv('.tmp/ka' + str(index) + '.csv')

  processTmpFiles(tables)


def processTmpFiles(tables):
  kaOutputFile = open('kaconfirmed.csv', 'w') 
  csvWriter = csv.writer(kaOutputFile, delimiter=',', quotechar='"')
  linesToWrite = []
  lineNumber = 0
  for index, table in enumerate(tables):
    kaFile = open('.tmp/ka' + str(index) + '.csv', 'r') 
    with open('.tmp/ka' + str(index) + '.csv', newline='') as kaFile:
      rowReader = csv.reader(kaFile, delimiter=',', quotechar='"')
      for row in rowReader:
        line = '|'.join(row)
        line = re.sub('^\|', '', line)
        if len(re.sub('^\|+', '', line)) == 0:
          continue
        if 'Page' in line:
          continue
#line = re.sub('\|$', '', re.sub('^\|+', '', line.replace('\"', '').replace(',,', ',')))
        
        linesArray = line.split('|')

        if category == "c":
          confirmedFileWriter(linesArray, linesToWrite)

        if category == "r":
          recoveredFileWriter(linesArray, linesToWrite)

        if category == "d":
          deceasedFileWriter(linesArray, linesToWrite)

    kaFile.close()
  for row in linesToWrite:
    csvWriter.writerow(row)
  kaOutputFile.close()


def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False


def confirmedFileWriter(linesArray, linesToWrite):
  '''
  if len(linesArray) != 8 or len(linesArray[5]) == 0:
    print("Ignoring {}".format(linesArray))
    return ""
  '''

  gender = ""
  if linesArray[5].strip() == 'Female':
    gender = 'F'
  elif linesArray[5].strip() == 'Male':
    gender = 'M'
  else:
    gender = 'Non-Binary'

  districtName = ""
  districtName = deltaCalculator.getNameMapping('Karnataka', linesArray[6])

  if len(linesArray[3]) == 0 and len(linesToWrite) != 0:
    print("Processing: {}".format(linesArray))
    for index, cellValue in enumerate(linesArray):
      if len(cellValue) > 0 and index == 4:
        linesToWrite[len(linesToWrite) - 1][2] = str(linesToWrite[len(linesToWrite) - 1][2]) + " " + str(cellValue)
      if len(cellValue) > 0 and index == 7:
        linesToWrite[len(linesToWrite) - 1][11] = str(linesToWrite[len(linesToWrite) - 1][11]) + " " + str(cellValue)
      if len(cellValue) > 0 and index == 6:
        linesToWrite[len(linesToWrite) - 1][5] = linesToWrite[len(linesToWrite) - 1][5] + " " + str(cellValue)
    return
  patientNumber = linesArray[3].replace('P-', 'KA-P') if 'P' in linesArray[3] else "KA-P" + str(linesArray[3])
    
  linesToWrite.append([patientNumber, datetime.date.today().strftime("%d/%m/%Y"), linesArray[4], gender, '', districtName, 'Karnataka', 'KA', 1, 'Hospitalized','', linesArray[7]])

def recoveredFileWriter(linesArray, linesToWrite):
  """
  if len(linesArray) < 3:
    print("Ignoring {} ".format(linesArray))
    return ""
  """

  districtName = linesArray[2].split('(')[0].strip()
  districtName = deltaCalculator.getNameMapping('Karnataka', districtName)

  patientIds = re.sub('\.', '', re.sub('&', ',', re.sub(' +', ',', linesArray[4])))
  patientIdArray = patientIds.split(',')

  if len(linesArray[2]) == 0 and len(linesToWrite) != 0 and len(patientIdArray) > 0:
    districtName = linesToWrite[len(linesToWrite) - 1][5]

  for item in patientIdArray:
    if len(item) == 0: #or is_number(item) or '(' in item:  
      continue
    if item == "\n":
      continue
    patientNumber = item.replace('P-', 'KA-P').replace('\n', '') if 'P' in item else "KA-P" + str(item)
    linesToWrite.append([patientNumber, datetime.date.today().strftime("%d/%m/%Y"), '', '','',districtName,'Karnataka', 'KA', 1, 'Recovered'])
#csvWriter.writerow([item.replace('P-', 'KA-P').replace('\n', ''), datetime.date.today().strftime("%d/%m/%Y"), '', '','',districtName,'Karnataka', 'KA', 1, 'Recovered'])
  

def deceasedFileWriter(linesArray, linesToWrite):
  """
  if len(linesArray) < 8 or len(linesArray[1]) == 0:
    print("Ignoring {} ".format(linesArray))
    return ""
  """
  if len(linesArray[0]) == 0:
    linesArray.pop(0)

#print(linesArray)
  districtName = linesArray[1].strip()
  districtName = deltaCalculator.getNameMapping('Karnataka', districtName)
  description = ""
  if len(linesArray) < 5:
    return
  for index, data in enumerate(linesArray):
    if index < 5:
      continue
    else:
      description = description + ";" + data if len(description) > 0 else data
#csvWriter.writerow(["KA-P" + str(linesArray[2]), datetime.date.today().strftime("%d/%m/%Y"), linesArray[3], linesArray[4], '', districtName, 'Karnataka', 'KA', 1, 'Deceased', '', description])
  if len(linesArray) > 3 and len(linesArray[2]) == 0 and len(linesToWrite) != 0:
    for index, cellValue in enumerate(linesArray):
      if len(cellValue) > 0 and index == 3:
        linesToWrite[len(linesToWrite) - 1][2] = str(linesToWrite[len(linesToWrite) - 1][2]) + " " + str(cellValue)
      if len(cellValue) > 0 and index == 4:
        linesToWrite[len(linesToWrite) - 1][3] = str(linesToWrite[len(linesToWrite) - 1][3]) + " " + str(cellValue)
    return
  linesToWrite.append(["KA-P" + str(linesArray[2]), datetime.date.today().strftime("%d/%m/%Y"), linesArray[3], linesArray[4], '', districtName, 'Karnataka', 'KA', 1, 'Deceased', '', description])

readPDF()

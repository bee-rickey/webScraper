#!/usr/bin/python3
import csv
import requests
import pdftotext
import sys
import os
import re
import logging
import camelot
from bs4 import BeautifulSoup
import html5lib
from deltaCalculator import DeltaCalculator


'''
To add a new state:

Make an entry into automation.meta file.
Write a function <StateCode>GetData()
Inside this function fetch/read files and prepare an array of hashes. 
Each hash should be of the format:
{
  "districtName": nameOfTheDistrict,
  "confirmed": TotalConfirmedCount,
  "recovered": TotalRecoveredCount,
  "deceased": TotalDeceasedCount
}
In case any of the values is unknown, pass -999 as the value. All keys are mandatory.

Pass these values to the deltaCalculator.getStateDataFromSite function with the state name. 
Eg: deltaCalculator.getStateDataFromSite("Arunachal Pradesh", districtArray, option). The value for options are: full/detailed/<empty>. These values are passed via command line.

The deltaCalculator object will return the valules to be added for today for the three categories across all districts mentioned.

In case there are name mappings required, i.e, if the district name in the bulletin and the district name in the site are different, make entries in nameMapping.meta file.
This file has <StateName>, <BulletinDistrictName>, <SiteDistrictName> as the format for each line.

For any pdf reading, refer to readFileFromURLV2 function. This needs to be called from within the <StateCode>GetData() function. 
'''



logging.basicConfig(filename='deltaCalculator.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
deltaCalculator = DeltaCalculator()
metaDictionary = {}
option = ""
typeOfAutomation = "url"
pdfUrl = ""
pageId = ""

''' This class holds the data from automation.meta file. This allows for better management of meta data '''
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
  
'''
def getAllColumnValues():
  columnSet = set()
  with open(".tmp/ct.txt", "r") as upFile:
    for line in upFile:
      for col in line.split('|')[1].split(','):
        columnSet.add(re.sub('\n', '', col.strip())
  return sorted(columnSet)
'''

def CTGetData():
  districtArray = []
  '''columnNumbers = getAllColumnValues()'''
  with open(".tmp/ct.txt", "r") as upFile:
    for line in upFile:
      linesArray = line.split('|')[0].split(',')
      availableColumns = line.split('|')[1].split(',')

      districtDictionary = {}
      districtDictionary['deceased'] = 0
      confirmedFound = False
      recoveredFound = False
      deceasedFound = False
      for index, data in enumerate(linesArray):
        if availableColumns[index].strip() == "2":
          districtDictionary['districtName'] = data.strip()
        if availableColumns[index].strip() == "4":
          districtDictionary['confirmed'] = int(data.strip())
          confirmedFound = True
        if availableColumns[index].strip() == "9":
          districtDictionary['recovered'] = int(data.strip())
          recoveredFound = True
        if availableColumns[index].strip() == "12": 
          districtDictionary['deceased'] += int(data.strip())
          deceasedFound = True

      if recoveredFound == False or confirmedFound == False:
        print("--> Issue with {}".format(linesArray))
        continue
      districtArray.append(districtDictionary)
  upFile.close()

  deltaCalculator.getStateDataFromSite("Chhattisgarh", districtArray, option)

def APGetData():
  if typeOfAutomation == "ocr":
    APGetDataByOCR()
  elif typeOfAutomation == "pdf":
    APGetDataByPdf()
  else:
    APGetDataByUrl()

def APGetDataByPdf():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  readFileFromURLV2(metaDictionary['Andhra Pradesh'].url, "Andhra Pradesh", "Anantapur", "")
  try:
    with open(".tmp/ap.csv", "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with {}".format(linesArray))
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districtArray.append(districtDictionary)

    upFile.close()
    deltaCalculator.getStateDataFromSite("Andhra Pradesh", districtArray, option)
  except FileNotFoundError:
    print("ap.csv missing. Generate through pdf or ocr and rerun.")

def APGetDataByOCR():
  districtArray = []
  with open(".tmp/ap.txt", "r") as upFile:
    for line in upFile:
      if 'Total' in line:
        continue

      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 6:
        print("--> Issue with {}".format(linesArray))
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

def ARGetDataByOcr():
  districtArray = []
  additionalDistrictInfo = {}
  additionalDistrictInfo['districtName'] = 'Papum Pare'
  additionalDistrictInfo['confirmed'] = 0
  additionalDistrictInfo['recovered'] = 0
  additionalDistrictInfo['deceased'] = 0

  with open(".tmp/ar.txt", "r") as upFile:
    for line in upFile:
      if 'Total' in line:
        continue

      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 12:
        print("--> Issue with {}".format(linesArray))
        continue


      if linesArray[0].strip() == "Capital Complex" or linesArray[0].strip() == "Papum Pare":
        additionalDistrictInfo['confirmed'] += int(linesArray[5])
        additionalDistrictInfo['recovered'] += int(linesArray[9])
        additionalDistrictInfo['deceased'] += int(linesArray[10]) if len(re.sub('\n', '', linesArray[10])) != 0 else 0
        continue

      districtDictionary = {}
      districtName = linesArray[0].strip()
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[5])
      districtDictionary['recovered'] = int(linesArray[9])
      districtDictionary['deceased'] = int(linesArray[10]) if len(re.sub('\n', '', linesArray[10])) != 0 else 0
      districtArray.append(districtDictionary)
  upFile.close()
  districtArray.append(additionalDistrictInfo)

  deltaCalculator.getStateDataFromSite("Arunachal Pradesh", districtArray, option)

def ARGetData():
  if typeOfAutomation == "ocr":
    ARGetDataByOcr()
    return
  stateDashboard = requests.request("get", metaDictionary['Arunachal Pradesh'].url).json()
  districtArray = []
  for districtDetails in stateDashboard:
    if districtDetails['district'] == 'Total':
      continue
    districtDictionary = {}
    districtDictionary['districtName'] =  districtDetails['district']
    districtDictionary['confirmed'] =  int(districtDetails['confirmed'])
    districtDictionary['recovered'] =  int(districtDetails['recovered'])
    districtDictionary['deceased'] =  int(districtDetails['deceased'])

    districtArray.append(districtDictionary)

  deltaCalculator.getStateDataFromSite("Arunachal Pradesh", districtArray, option)

def APGetDataByUrl():
  response = requests.request("GET", metaDictionary['Andhra Pradesh'].url)
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find_all("table")[1].find_all("tr")

  districtArray = []
  for index, row in enumerate(table):
    data = row.find_all("td")
    if 'Total' in data[0].get_text() or 'District' in data[0].get_text():
      continue

    districtDictionary = {}
    districtDictionary['districtName'] =  data[0].get_text()
    districtDictionary['confirmed'] =  int(data[1].get_text())
    districtDictionary['recovered'] =  int(data[2].get_text())
    districtDictionary['deceased'] =  int(data[3].get_text())
    districtArray.append(districtDictionary)

  """
  stateDashboard = requests.request("post", metaDictionary['Andhra Pradesh'].url).json()

  for districtDetails in (stateDashboard['cases_district']):
    districtDictionary = {}
    districtDictionary['districtName'] =  districtDetails['district_name']
    districtDictionary['confirmed'] =  int(districtDetails['cases'])
    districtDictionary['recovered'] =  int(districtDetails['recovered'])
    districtDictionary['deceased'] =  int(districtDetails['death'])

    districtArray.append(districtDictionary)
  """
  deltaCalculator.getStateDataFromSite("Andhra Pradesh", districtArray, option)

def ORGetData():
  os.system("curl -sk https://health.odisha.gov.in/js/distDtls.js | grep -i 'District_id' | sed 's/\"//g' | sed 's/,/:/g'| cut -d':' -f4,8,12,14,16,18,22 |sed 's/:/,/g' > orsite.csv")

  districtArray = []
  with open("orsite.csv", "r") as metaFile:
    for line in metaFile:
      districtDictionary = {}
      lineArray = line.strip().split(',') 
      districtDictionary['districtName'] = lineArray[0].strip()
      districtDictionary['confirmed'] = int(lineArray[1].strip())
      districtDictionary['recovered'] = int(lineArray[2].strip())
      # Deceased due to other reasons also to deceased count
      districtDictionary['deceased'] = int(lineArray[3].strip()) + int(lineArray[4].strip())
    
      districtArray.append(districtDictionary)

  deltaCalculator.getStateDataFromSite("Odisha", districtArray, option)

def MHGetData():
  if typeOfAutomation == "ocr":
    MHGetDataByOcr()
  else:
    MHGetDataByUrl()

def MHGetDataByOcr():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  try:
    with open(".tmp/mh.txt", "r") as upFile:
      isIgnoreFlagSet = False
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if 'Total' in line or isIgnoreFlagSet == True:
          isIgnoreFlagSet = True
          print("--> Ignoring {} ".format(line))
        if len(linesArray) < 5:
          print("--> Ignoring due to invalid length: {}".format(linesArray))
          continue
        districtDictionary = {}
        try:
          if is_number(linesArray[0].strip()):
            print("--> Ignoring: {}".format(linesArray))
            continue

          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[1])
          districtDictionary['recovered'] = int(linesArray[2])
          districtDictionary['deceased'] = int(linesArray[3])
          districtArray.append(districtDictionary)
        except ValueError:
          print("--> Ignoring: {}".format(linesArray))
          continue

    upFile.close()
    deltaCalculator.getStateDataFromSite("Maharashtra", districtArray, option)
  except FileNotFoundError:
    print("rj.txt missing. Generate through pdf or ocr and rerun.")

def MHGetDataByUrl():
  stateDashboard = requests.request("get", metaDictionary['Maharashtra'].url).json()

  districtArray = []
  for districtDetails in stateDashboard:
    districtDictionary = {}
    districtDictionary['districtName'] = districtDetails['District']
    districtDictionary['confirmed'] = districtDetails['Positive Cases']
    districtDictionary['recovered'] = districtDetails['Recovered']
    districtDictionary['deceased'] = districtDetails['Deceased']
    districtArray.append(districtDictionary)

  deltaCalculator.getStateDataFromSite("Maharashtra", districtArray, option)

def HPGetData():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  districtTableBeingRead = False
  try:
    with open(".tmp/hp.txt", "r") as upFile:
      for line in upFile:
        line = re.sub('\*', '', line)
        linesArray = line.split('|')[0].split(',')
        availableColumns = line.split('|')[1].split(',')

        '''
        if 'Report of Positive Cases till date' in (re.sub(" +", " ", " ".join(linesArray))):
          districtTableBeingRead = True

        if districtTableBeingRead == False or 'Total' in linesArray[0]:
          districtTableBeingRead = False
          continue
        '''

        districtDictionary = {}
        confirmedFound = False
        recoveredFound = False
        deceasedFound = False
        '''
        for index, data in enumerate(linesArray):
          try:
            if availableColumns[index].strip() == "1":
              districtDictionary['districtName'] = data.strip()
            if availableColumns[index].strip() == "2":
              districtDictionary['confirmed'] = int(data.strip())
              confirmedFound = True
            if availableColumns[index].strip() == "6":
              districtDictionary['recovered'] = int(data.strip())
              recoveredFound = True
            if availableColumns[index].strip() == "7":
              districtDictionary['deceased'] = int(data.strip())
              deceasedFound = True
          except ValueError:
            print("--> Ignoring {}".format(linesArray))
            continue

        if recoveredFound == False or confirmedFound == False or deceasedFound == False:
          print("--> Issue with {}".format(linesArray))
          continue
        '''

        if len(linesArray) != 10:
          print("--> Issue with {}".format(linesArray))
          continue

        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1].strip())
        districtDictionary['recovered'] = int(linesArray[7].strip())
        districtDictionary['deceased'] = int(re.sub('\*', '', linesArray[8].strip()).strip())

        districtArray.append(districtDictionary)

    upFile.close()
    deltaCalculator.getStateDataFromSite("Himachal Pradesh", districtArray, option)
  except FileNotFoundError:
    print("hp.txt missing. Generate through pdf or ocr and rerun.")
    

def RJGetDataUsingUrl():
  if typeOfAutomation != "ocr" or typeOfAutomation != "pdf":
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
  errorCount = 0
  linesArray = []
  districtDictionary = {}
  districtArray = []
  masterColumnArray = []
  splitArray = []
  lengthOfArray = 7    
  activeIndex = 6
  recoveredIndex = 3
  deceasedIndex = 5
  global typeOfAutomation

  if typeOfAutomation == "ocr1":
    lengthOfArray = 7    
    activeIndex = 6
    recoveredIndex = 3
    deceasedIndex = 5
  else:
    typeOfAutomation = "ocr2"
    lengthOfArray = 8    
    activeIndex = 7
    recoveredIndex = 4
    deceasedIndex = 6
  print("--> Using format {}".format(typeOfAutomation))
    
  try:
    with open(".tmp/up.txt", "r") as upFile:
      for line in upFile:
        splitArray = re.sub('\n', '', line.strip()).split('|')
        linesArray = splitArray[0].split(',')

        if errorCount > 10:
          errorCount = 0
          if typeOfAutomation == "ocr1":
            typeOfAutomation = "ocr2"
          else:
            typeOfAutomation = "ocr1"
          print("--> Switching to version {}. Error count breached.".format(typeOfAutomation))
          UPGetData()
          return

        if len(linesArray) != lengthOfArray:
          print("--> Issue with {}".format(linesArray))
          errorCount += 1
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[recoveredIndex]) + int(linesArray[deceasedIndex]) + int(linesArray[activeIndex])
        districtDictionary['recovered'] = int(linesArray[recoveredIndex])
        districtDictionary['deceased'] = int(linesArray[deceasedIndex])
        """

        districtDictionary['confirmed'] = int(linesArray[2]) 
        districtDictionary['recovered'] = int(linesArray[4])
        districtDictionary['deceased'] = int(linesArray[6])
        """

        districtArray.append(districtDictionary)
    upFile.close()

    deltaCalculator.getStateDataFromSite("Uttar Pradesh", districtArray, option)
  except FileNotFoundError:
    print("up.txt missing. Generate through pdf or ocr and rerun.")

def UTGetData():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  ignoreLines = False
  try:
    with open(".tmp/ut.txt", "r") as upFile:
      for line in upFile:
        if ignoreLines == True:
          continue

        if 'Total' in line:
          ignoreLines = True
          continue

        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 7:
          print("--> Issue with {}".format(linesArray))
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[4])
        districtArray.append(districtDictionary)

    upFile.close()
    deltaCalculator.getStateDataFromSite("Uttarakhand", districtArray, option)
  except FileNotFoundError:
    print("br.txt missing. Generate through pdf or ocr and rerun.")

def BRGetData():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  try:
    with open(".tmp/br.txt", "r") as upFile:
      for line in upFile:
        linesArray = line.split('|')[0].split(',')
        if len(linesArray) != 5:
          print("--> Issue with {}".format(linesArray))
          continue
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
        if len(linesArray) < 7:
          print("--> Issue with {}".format(linesArray))
          continue

        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[4]) + int(linesArray[5])
        districtDictionary['recovered'] = int(linesArray[2]) + int(linesArray[6])
        districtDictionary['deceased'] = int(linesArray[3]) + int(linesArray[7])

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

        if len(linesArray) != 12:
          print("--> Issue with {}".format(linesArray))
          continue
        
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
          print("--> Ignoring {} ".format(line))
        if len(linesArray) != 8:
          print("--> Ignoring due to invalid length: {}".format(linesArray))
          continue
        districtDictionary = {}
        try:
          if is_number(linesArray[0].strip()):
            print("--> Ignoring: {}".format(linesArray))
            continue

          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[2])
          districtDictionary['recovered'] = int(linesArray[6])
          districtDictionary['deceased'] = int(linesArray[4])
          districtArray.append(districtDictionary)
        except ValueError:
          print("--> Ignoring: {}".format(linesArray))
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
          print("--> Ignoring due to invalid length: {}".format(linesArray))
          continue
        districtDictionary = {}
        try:
          if is_number(linesArray[0].strip()):
            print("--> Ignoring: {}".format(linesArray))
            continue

          districtDictionary['districtName'] = linesArray[0].strip().title()
          districtDictionary['confirmed'] = int(linesArray[6])
          districtDictionary['recovered'] = int(linesArray[9])
          districtDictionary['deceased'] = int(linesArray[10])
          districtArray.append(districtDictionary)
        except ValueError:
          print("--> Ignoring: {}".format(linesArray))
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
    with open(".tmp/wb.csv", "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with {}".format(linesArray))
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districtArray.append(districtDictionary)

    upFile.close()
    deltaCalculator.getStateDataFromSite("West Bengal", districtArray, option)
  except FileNotFoundError:
    print("wb.txt missing. Generate through pdf or ocr and rerun.")

def PBGetDataThroughPdf():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  readFileFromURLV2(metaDictionary['Punjab'].url, "Punjab", "Ludhiana", "Total")
  try:
    with open(".tmp/pb.csv", "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 5:
          print("--> Issue with {}".format(linesArray))
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
          print("--> Issue with {}".format(linesArray))
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
  global pdfUrl
  global pageId
  linesArray = []
  districtDictionary = {}
  districtArray = []
  runDeceased = False
  startId = 0
  endId = 0

  if ',' in pageId:
    startId = pageId.split(',')[1]
    endId = pageId.split(',')[2]
    pageId = pageId.split(',')[0]
    runDeceased = True

  if len(pdfUrl) != 0:
    urlArray = pdfUrl.split('/')
    for index, parts in enumerate(urlArray):
      if parts == "file":
        if urlArray[index + 1] == "d":
          fileId = urlArray[index + 2]
          break
    pdfUrl = "https://docs.google.com/uc?export=download&id=" + fileId 
    print("--> Downloading using: {}".format(pdfUrl))  
  readFileFromURLV2('', "Karnataka", "Bagalakote", "Total")
  try:
    with open(".tmp/ka.csv", "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with {}".format(linesArray))
          continue
        districtDictionary = {}
        districtDictionary['districtName'] = linesArray[0].strip()
        districtDictionary['confirmed'] = int(linesArray[1])
        districtDictionary['recovered'] = int(linesArray[2])
        districtDictionary['deceased'] = int(linesArray[3]) if len(re.sub('\n', '', linesArray[3])) != 0 else 0
        districtArray.append(districtDictionary)

    upFile.close()
    deltaCalculator.getStateDataFromSite("Karnataka", districtArray, option)

    if runDeceased == True:
      os.system("python3 kaautomation.py d " + str(startId) + " " + str(endId) + " && cat kaconfirmed.csv")

  except FileNotFoundError:
    print("ka.txt missing. Generate through pdf or ocr and rerun.")

def HRGetData():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  if typeOfAutomation == "pdf":
    readFileFromURLV2(metaDictionary['Haryana'].url, "Haryana", "Faridabad", "Total")
  try:
    with open(".tmp/hr.csv", "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with {}".format(linesArray))
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
    print("hr.csv missing. Generate through pdf or ocr and rerun.")
      
def TNGetData():
  linesArray = []
  districtDictionary = {}
  districtArray = []
  if typeOfAutomation == "ocr":
    getTNDataThroughOcr()
    return
  else:
    convertTnPDFToCSV()
  try:
    with open(".tmp/tn.csv", "r") as upFile:
      for line in upFile:
        linesArray = line.split(',')
        if len(linesArray) != 4:
          print("--> Issue with {}".format(linesArray))
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

def getTNDataThroughOcr():
  districtArray = []
  linesArray = []
  airportDictionary = {'districtName': 'Airport Quarantine', "confirmed": 0, "recovered": 0, "deceased": 0}
  with open(".tmp/tn.txt") as tnFile:
    for line in tnFile:
      line = line.replace('"', '').replace('*', '').replace('#', '').replace('$', '')
      linesArray = line.split('|')[0].split(',')
      if len(linesArray) != 5:
        print("--> Issue with {}".format(linesArray))
        continue

      if 'Airport' in line:
        airportDictionary['confirmed'] += int(linesArray[1])
        airportDictionary['recovered'] += int(linesArray[2])
        airportDictionary['deceased'] += int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
        continue

      if 'Railway' in line:
        linesArray[0] = 'Railway Quarantine'

      districtDictionary = {}
      districtDictionary['districtName'] = linesArray[0].strip()
      districtDictionary['confirmed'] = int(linesArray[1])
      districtDictionary['recovered'] = int(linesArray[2])
      districtDictionary['deceased'] = int(linesArray[4]) if len(re.sub('\n', '', linesArray[4])) != 0 else 0
      districtArray.append(districtDictionary)

    districtArray.append(airportDictionary)
    tnFile.close()
    print(districtArray)
    deltaCalculator.getStateDataFromSite("Tamil Nadu", districtArray, option)



def NLGetData():
  response = requests.request("GET", metaDictionary['Nagaland'].url)
  soup = BeautifulSoup(response.content, 'html.parser')
  districtArray = []
  for row in soup.find_all("tr"):
    districtDictionary = {}
    for index, data in enumerate(row.find_all("td")):
      if index == 0:
        if len(data.get_text().strip().title()) == 0:
          continue
        districtDictionary['districtName'] = data.get_text().strip().title()
      if index == 5:
        if 'districtName' not in districtDictionary:
          continue
        districtDictionary['active'] = int(data.get_text().strip())
        districtDictionary['confirmed'] = -999
        districtDictionary['recovered'] = -999
        districtDictionary['deceased'] = -999
        districtArray.append(districtDictionary)

  deltaCalculator.getStateDataFromSite("Nagaland", districtArray, option)

def GAGetData():
  response = requests.request("GET", metaDictionary['Goa'].url)
  soup = BeautifulSoup(response.content, 'html.parser')
  table = soup.find_all("div", {"class": "vc_col-md-2"})

  districtArray = []
  for index, row in enumerate(table):
    print(row.get_text())
      
    districtDictionary = {}
    districtArray.append(districtDictionary)

  return
  deltaCalculator.getStateDataFromSite("Goa", districtArray, option)

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
    districtDictionary['deceased'] = int(dataPoints[4].get_text().strip())
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
  confirmedArray = re.sub('\\r', '', re.sub(':', '', re.sub(' +', ' ', re.sub("\n", " ", confirmed.get_text().strip())))).split(' ')
  dischargedArray = re.sub('\\r', '', re.sub(':', '', re.sub(' +', ' ', re.sub("\n", " ", discharged.get_text().strip())))).split(' ')

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
      
def PBFormatLine(row):
  return row[1] + "," + row[2] + "," + row[3] + "," + row[4] + "," + row[5] + "\n"

def KAFormatLine(row):
  district = ""
  modifiedRow = []
  for value in row:
    if len(value) > 0:
      modifiedRow.append(value)

  if is_number(modifiedRow[0]) == False:
    district = " ".join(re.sub(' +', ' ', modifiedRow[0]).split(' ')[1:])
    modifiedRow.insert(0, 'a')
  else:
    district = re.sub('\*', '', modifiedRow[1])
  print(modifiedRow)

  return district + "," + modifiedRow[3] + "," + modifiedRow[5] + "," + modifiedRow[8] + "\n"

"""
def HRFormatLine(line):
  line = re.sub(' +', ',', re.sub('^ +', '', line))

  linesArray = line.split(',')

  if len(linesArray) > 1 and linesArray[1] == "Charkhi":
    linesArray.remove("Dadri")
    linesArray[1] = "Charkhi Dadri"

  if len(linesArray) != 11:
    print("--> Ignoring: {}".format(linesArray))
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
"""

def HRFormatLine(row):
  row[1] = re.sub('\*', '', row[1])
  if '[' in row[3]:
    row[3] = row[3].split('[')[0]
  if '[' in row[4]:
    row[4] = row[4].split('[')[0]
  if '[' in row[7]:
    row[7] = row[7].split('[')[0]
  if '[' in row[6]:
    row[6] = row[6].split('[')[0]

  line = row[1] + "," + row[3] + "," + row[4] + "," + str(int(row[6]) + int (row[7])) + "\n"
  return line

def APFormatLine(row):
  line = row[1] + "," + row[3] + "," + row[5] + "," + row[6] + "\n"
  return line


def WBFormatLine(row):
  row[2] = re.sub(',', '', re.sub('\+.*', '', row[2]))
  row[3] = re.sub(',', '', re.sub('\+.*', '', row[3]))
  row[4] = re.sub('\#', '', re.sub(',', '', re.sub('\+.*', '', row[4])))
  row[5] = re.sub(',', '', re.sub('\+.*', '', row[5]))
  line = row[1] + "," + row[2] + "," + row[3] + "," + row[4] + "\n"
  return line

''' 
  This method uses camelot package to read a pdf and then parse it into a csv file.
  In this method, we read the pdf either from the meta file or from the pdfUrl global variable. This variable can be set from the cmd line.
  The method also takes user input for page number or allows for page number to be used from the pageId global variable.
  The method, reads a specific page, then for that page, decides if a line has to be ignored using starting and ending keys. 
  Then the method calls a "<stateCode>FormatLine(row)" function that calls the corresponding function to allow for any row/line to be manipulated.
  The outputs are written to a <stateCode>.csv file. This is read inside the corresponding <stateCode>GetData() functions which call deltaCalculator to calculate deltas.
'''
def readFileFromURLV2(url, stateName, startKey, endKey):
  global pdfUrl
  global pageId
  stateFileName = metaDictionary[stateName].stateCode 

  if len(pdfUrl) > 0:
    url = pdfUrl
  if len(url) > 0:
    print("--> Requesting download from {} ".format(url))
    r = requests.get(url, allow_redirects=True)
    open(".tmp/" + stateFileName + ".pdf", 'wb').write(r.content)
  if len(pageId) > 0:
    pid = pageId
  else:
    pid = input("Enter district page:")
  tables = camelot.read_pdf(".tmp/" + stateFileName + ".pdf", strip_text = '\n', pages = pid)
  for index, table in enumerate(tables):
    tables[index].to_csv('.tmp/' + stateFileName + str(index) + '.pdf.txt')

  stateOutputFile = open('.tmp/' + stateFileName.lower() + '.csv', 'w')
  csvWriter = csv.writer(stateOutputFile)
  arrayToWrite = []

  startedReadingDistricts = False
  for index, table in enumerate(tables):
    with open('.tmp/' + stateFileName + str(index) + '.pdf.txt', newline='') as stateCSVFile:
      rowReader = csv.reader(stateCSVFile, delimiter=',', quotechar='"')
      for row in rowReader:
        line = "|".join(row)
        line = re.sub("\|+", '|', line)
        if startKey in line:
          startedReadingDistricts = True
        if len(endKey) > 0 and endKey in line:
          startedReadingDistricts = False
          continue
        if startedReadingDistricts == False:
          continue

        line = eval(stateFileName + "FormatLine")(line.split('|'))
        if line == "\n":
          continue
        print(line, file = stateOutputFile, end = "")

  stateOutputFile.close()
        
''' This will be deprecated. '''
def readFileFromURL(url, stateName, startKey, endKey):
  global pdfUrl
  global pageId
  stateFileName = metaDictionary[stateName].stateCode 
  if len(pdfUrl) > 0:
    url = pdfUrl

  if len(url) > 0:
    r = requests.get(url, allow_redirects=True)
    open(".tmp/" + stateFileName + ".pdf", 'wb').write(r.content)

  with open(".tmp/" + stateFileName + ".pdf", "rb") as f:
    pdf = pdftotext.PDF(f)

  fileToWrite = open(".tmp/" + stateFileName + ".pdf.txt", "w")
  if len(pageId) > 0:
    pid = pageId
  else:
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

'''This will eventually be moved to TNFormatLine(row) function'''
def convertTnPDFToCSV():
  global pdfUrl
  global typeOfAutomation

  if len(pdfUrl) > 0:
    r = requests.get(pdfUrl, allow_redirects=True)  
    open(".tmp/tn.pdf", 'wb').write(r.content)

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
        print("--> Ignoring line: {} due to less columns".format(line))
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
  global pdfUrl
  global pageId

  if len(sys.argv) not in [1, 2, 3, 4]:
    print('Usage: ./automation "[StateName]" "[detailed/full]" "[ocr/pdf=url]"')
    return

  if len(sys.argv) == 2:
    stateName = sys.argv[1]

  if len(sys.argv) == 3:
    stateName = sys.argv[1]
    option = sys.argv[2]

  if len(sys.argv) == 4:
    stateName = sys.argv[1]
    option = sys.argv[2]
    if "=" in sys.argv[3]:
      typeOfAutomation = sys.argv[3].split("=")[0]
      pdfUrl = sys.argv[3].split("=")[1]
      if len(sys.argv[3].split("=")) > 2:
        pageId = sys.argv[3].split("=")[2]
    else:
      typeOfAutomation = sys.argv[3]
  
  print("Using pageId: {}".format(pageId))
  
  if not stateName:
    stateName = "All States"
  fetchData(stateName)

if __name__ == '__main__':
  main()


import sys
import json
from PIL import Image
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.patches as patches

dataDictionary = {}
dataDictionaryArray = []
translationDictionary = {}
xInterval = 0
xStartThreshold = 0
yStartThreshold = 0
xEndThreshold = 0
yEndThreshold = 0
configxInterval = 0
configyInterval = 0
yInterval = 0
startingText = ""
endingText = ""
enableTranslation = False
translationFile = ""
fileName = ""
xWidthTotal = 0


def is_number(s):
	try:            
		int(s)
		return True
	except ValueError:
		return False

class cellItem:
	def __init__(self, value, x, y, lbx, lby, w, h, col, row, index):
		self.value = value
		self.x = x
		self.y = y
		self.col = col
		self.row = row
		self.index = index
		self.lbx = lbx
		self.lby = lby
		self.h = h
		self.w = w

def buildCellsV2():
	global xInterval
	global yInterval
	global startingText
	global endingText
	global yStartThreshold
	global xStartThreshold
	global configxInterval
	global configyInterval
	global xWidthTotal
# testingNumbersFile = open("poly.txt", "r")
#data = json.load(testingNumbersFile)

def buildCells():
	global xInterval
	global yInterval
	global startingText
	global endingText
	global xStartThreshold
	global yStartThreshold
	global xEndThreshold
	global yEndThreshold
	global configxInterval
	global configyInterval
	global xWidthTotal

	startingMatchFound = False
	endingMatchFound = False

	autoEndingText = endingText
	autoStartingText = startingText


	testingNumbersFile = open("bounds.txt", "r")
	for index, line in enumerate(testingNumbersFile):
		lineArray = line.split('|')
		if len(lineArray) != 6:
			continue

		lowerLeft = []
		lowerRight = []
		upperRight = []
		upperLeft = []
		
		if not lineArray[0] or not lineArray[2] or not lineArray[4] or not lineArray[5]:
			continue

		value = lineArray[0]
			
		lowerLeft = lineArray[2].split(',')
		lowerRight = lineArray[3].split(',')
		upperRight = lineArray[4].split(',')
		upperLeft = lineArray[5].split(',')

#Get the mid point of the bound where the text matches
		xMean = (int(lowerLeft[0]) + int(lowerRight[0]))/2
		yMean = (int(lowerLeft[1]) + int(upperLeft[1]))/2

		if startingText == "auto":
			if value in translationDictionary:
				if xStartThreshold == 0:
					xStartThreshold = xMean
					autoStartingText = value
				if yStartThreshold == 0:
					yStartThreshold = yMean

				if yMean < yStartThreshold:
					xStartTreshold = xMean 
					yStartThreshold = yMean
					autoStartingText = value
					

		if endingText == "auto":
			if value in translationDictionary:
				if xEndThreshold == 0:
					xEndThreshold = xMean
				if yEndThreshold == 0:
					yEndThreshold = yMean
					autoEndingText = value

				if yMean > yEndThreshold:
					xEndThreshold = xMean
					yEndThreshold = yMean
					autoEndingText = value

		if ',' in startingText:
			if value in startingText.split(','):# and startingMatchFound == False:
				startingMatchFound = True
				xStartThreshold = xMean
				yStartThreshold = yMean  
		else:
			if value == startingText and startingMatchFound == False:
				startingMatchFound = True
				xStartThreshold = xMean
				yStartThreshold = yMean  

		if ',' in endingText:
			if value in endingText.split(','):# and endingMatchFound == False:
				endingMatchFound = True
				xEndThreshold = xMean
				yEndThreshold = yMean
		else:
			if value == endingText and endingMatchFound == False:
				endingMatchFound = True
				xEndThreshold = xMean
				yEndThreshold = yMean

#Use these intervals as a possible error in mid point calculation
		xInterval = (int(lowerRight[0]) - int(lowerLeft[0]))/2 if (int(lowerRight[0]) - int(lowerLeft[0]))/2 > xInterval else xInterval
		yInterval = (int(upperLeft[1]) - int(lowerLeft[1]))/2 if (int(upperLeft[1]) - int(lowerLeft[1]))/2 > yInterval else yInterval
		xWidthTotal = xWidthTotal + int(lowerRight[0]) - int(lowerLeft[0])
		dataDictionaryArray.append(cellItem(value, xMean, yMean, lowerLeft[0], lowerLeft[1], (float(lowerRight[0]) - float(lowerLeft[0])), (float(upperLeft[1]) - float(lowerLeft[1])), 0, 0, index + 1))
	xWidthTotal = xWidthTotal/len(dataDictionaryArray)
	startingText = autoStartingText
	endingText = autoEndingText
	testingNumbersFile.close()

def buildReducedArray():
	global endingText
	tempDictionaryArray = []
	global xInterval
	global yInterval
	global dataDictionaryArray
	maxWidth = 0
	maxHeight = 0

#Ignore the texts that lie to the left and top of the threshold text. This improves accuracy of output
	print("Starting text: {} ... Ending text: {}".format(startingText, endingText)) 
	for cell in dataDictionaryArray:
		if cell.y < yStartThreshold - 10 or cell.x < xStartThreshold - 30:
			continue

		if len(endingText) != 0 and (cell.y > yEndThreshold + 10 or cell.x < xEndThreshold - 30):
			continue

		tempDictionaryArray.append(cell)
		maxWidth = cell.w if cell.w > maxWidth else maxWidth
		maxHeight = cell.h if cell.h > maxHeight else maxHeight

	xInterval = maxWidth/2
	yInterval = maxHeight/2
	
	dataDictionaryArray = tempDictionaryArray

def assignRowsAndColumns():
	global yInterval
	global xInterval
	global configyInterval
	global configxInterval


	if configxInterval != 0:
		xInterval = configxInterval
	if configyInterval != 0:
		yInterval = configyInterval

	print("Using computed yInterval: {}, xInterval: {}".format(yInterval, xInterval))
	for rowIndex, currentCell in enumerate(dataDictionaryArray):           

		if currentCell.row == 0:
			currentCell.row = rowIndex + 1
		for colIndex, restOfTheCells in enumerate(dataDictionaryArray):

			if currentCell.col == 0:
				currentCell.col = rowIndex + 1
			if restOfTheCells.index == currentCell.index:
				continue

			yUpperBound = currentCell.y + yInterval
			yLowerBound = currentCell.y - yInterval
#If the y coordinate matches, the texts lie on the same row
			if restOfTheCells.row == 0:
				if yLowerBound <= restOfTheCells.y <= yUpperBound:
					restOfTheCells.row = rowIndex + 1

			xUpperBound = currentCell.x + xInterval
			xLowerBound = currentCell.x - xInterval

#If the x coordinate matches, the texts lie on the same column
			if restOfTheCells.col == 0:
				if xLowerBound <= restOfTheCells.x <= xUpperBound:
					restOfTheCells.col = currentCell.col
			

def buildTranslationDictionary():
	global startingText
	global endingText

	originalStartingText = startingText
	originalEndingText = endingText

	with open(translationFile, "r") as metaFile:
		for line in metaFile:
			if line.startswith('#'):
				continue
			lineArray = line.strip().split(',')
			if len(startingText) != 0:
				if originalStartingText.strip() == lineArray[1].strip():
					startingText = startingText + "," + lineArray[0].strip() 

			if len(endingText) != 0:
				if originalEndingText.strip() == lineArray[1].strip():
					endingText = endingText + "," + lineArray[0].strip() 

			translationDictionary[lineArray[0].strip()] = lineArray[1].strip()
	

def printOutput():
	outputFile = open('output.txt', 'w') 
	global enableTranslation
	xArray = []
	yArray = []

	image = np.array(Image.open(fileName), dtype=np.uint8)
	fig, ax = plt.subplots(1)

	for i in range(0, len(dataDictionaryArray)):
		outputString = []
		for cell in dataDictionaryArray:
			if cell.row == i:
				outputString.append(cell)
		outputString.sort(key=lambda x: x.x)

		output = ""
		previousCol = -999
		mergedValue = ""
#<TODO> column verification has to come in here
#Merge those texts separated by spaces - these have the same column value due to proximity but belong to different objects
		columnList = ""
		for index, value in enumerate(outputString):
			if index == 0:
				mergedValue = value.value 
				previousCol = value.col
				columnList = str(value.col)
				rect = patches.Rectangle((int(value.lbx), int(value.lby)), value.w, value.h,linewidth=0.75,edgecolor='r', facecolor='none')
				ax.add_patch(rect)
				continue

			if value.col == previousCol and is_number(value.value) == False:
				mergedValue = mergedValue + " " + value.value if len(mergedValue) != 0 else value.value
				if index == len(outputString) - 1:
					output += mergedValue if len(output) == 0 else " , " + mergedValue
			else:
				if index == len(outputString) - 1:
					mergedValue = mergedValue + ", " + value.value if len(mergedValue) != 0 else value.value
				output += mergedValue if len(output) == 0 else " , " + mergedValue
				previousCol = value.col
				mergedValue = value.value #+ " ---- " + str(value.col)
				columnList = columnList + ", " + str(value.col) if len(columnList) != 0 else str(value.col)
				rect = patches.Rectangle((int(value.lbx), int(value.lby)), value.w, value.h,linewidth=0.75,edgecolor='r', facecolor='none')
				ax.add_patch(rect)

		if len(output) > 0:
			if enableTranslation == False:
				print("{} | {}".format(output, columnList), file = outputFile)
			else:
				outputArray = output.split(',')
				districtIndex = 0
#If the rows are not numberd, this condition can be skipped. For UP bulletin, this makes sense.
				if(is_number(outputArray[0])):
					districtName = outputArray[1].strip()
					distrinctIndex = 1
				else:
					districtName = outputArray[0].strip()
					distrinctIndex = 0

#Do a lookup for district name, if not found, discard the record and print a message.
				try:
					translatedValue = translationDictionary[districtName]
					outputString = translatedValue 
					for index, value in enumerate(outputArray):
						if index > districtIndex: #and is_number(value):
							outputString += "," + value.strip()
					print("{} | {}".format(outputString, columnList), file = outputFile)
				except KeyError:
					print("Failed to find lookup for {} ".format(districtName))  
	outputFile.close()
	ax.imshow(image)
	plt.show()

def parseConfigFile(fileName):
	global startingText
	global endingText
	global enableTranslation
	global translationFile
	global configyInterval
	global configxInterval

	configFile = open(fileName, "r")
	for index, line in enumerate(configFile):
		lineArray = line.split(':')
		if len(lineArray) < 2:
			continue

		key = lineArray[0].strip()
		value = lineArray[1].strip()
	
		if key == "startingText":
			if ',' in value:
				startingText = value.split(',')[0]
				endingText = value.split(',')[1]
			else:
				startingText = value
		if key == "enableTranslation":
			enableTranslation = eval(value)
		if key == "translationFile":
			translationFile = value
		if key == "xInterval":
			configxInterval = int(value)
		if key == "yInterval":
			configyInterval = int(value)

def main():
	global startingText
	global endingText
	global enableTranslation
	global fileName
# If given, this text will be used to ignore those items above and to the left of this text. This can cause issues if the text is repeated!
	if len(sys.argv) > 1:
		parseConfigFile(sys.argv[1])
		fileName = sys.argv[2]
				
	buildTranslationDictionary()

	buildCells()
	buildCellsV2()

	if len(startingText) != 0 or len(endingText) != 0:
		buildReducedArray()

	assignRowsAndColumns()
	printOutput()

if __name__ == '__main__':
  main()

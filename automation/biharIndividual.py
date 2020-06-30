#!/usr/bin/python3

testingNumbersFile = open("ocr/output.txt", "r")

for index, line in enumerate(testingNumbersFile):
	if index == 0:
		continue
	outputString = ""
	linesArray = line.split('|')[0].split(',')

	gender = "F" if linesArray[1].strip() == "FEMALE" else "M"
	print("{}, {}, {}, {}, {}, {}, {}, {}".format(linesArray[2].strip(), gender, linesArray[3].strip().title(), linesArray[4].strip().title(), 'Bihar', 'BR', 1, 'Hospitalized'))

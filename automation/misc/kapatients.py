import requests
import pdftotext
import PyPDF2 as pypdf
import camelot
import re
import datetime
import matplotlib.pyplot as plt
from deltaCalculator import DeltaCalculator


def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

tables = camelot.read_pdf('ka.pdf',strip_text='\n', pages="5,6,7,8", split_text = True)

print(len(tables))
for index, table in enumerate(tables):
	tables[index].to_csv('ka' + str(index) + '.csv')

kaOutputFile = open('kafull.csv', 'w') 
for index, table in enumerate(tables):
	kaFile = open('ka' + str(index) + '.csv', 'r') 
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

		print("{},{},{},{},{},{},{},{},{},{},{}".format(linesArray[4].replace('P-', 'KA-P'), datetime.date.today().strftime("%d/%m/%Y"), linesArray[5], gender,'',linesArray[7],'Karnataka', 'KA', 1, 'Hospitalized',linesArray[8]), file = kaOutputFile)

kaOutputFile.close()

##camelot.plot(tables[0], kind = "contour")
#plt.show()


"""
pdfobject=open('ka.pdf','rb')
pdf=pypdf.PdfFileReader(pdfobject)
print(pdf.extractText())

url = "http://www.nhmharyana.gov.in/WriteReadData/userfiles/file/CoronaVirus/Daily%20Bulletin%20of%20COVID%2019%20as%20on%209-06-2020%20Evening.pdf"
r = requests.get(url, allow_redirects=True)
open('hr.pdf', 'wb').write(r.content)

with open("ka.pdf", "rb") as f:
    pdf = pdftotext.PDF(f)

recoveryKa = open("ka.pdf.txt", "w")
pid = input("Enter district page:")
print(pdf[int(pid)] , file = recoveryKa)
recoveryKa.close()

tnFile = open('ka.pdf.txt', 'r') 
lines = tnFile.readlines() 
tnOutputFile = open('ka.csv', 'w') 

startedReadingDistricts = False
for line in lines:
	if len(line) == 0:
		continue
	print(line)

	if 'Yadagiri' in line:
		startedReadingDistricts = True
	if 'Total' in line:
		startedReadingDistricts = False
		continue
	if startedReadingDistricts == False:
		continue
	
	line = re.sub(' +', ',', re.sub('^ +', '', line))

	linesArray = line.split(',')
	print(linesArray)

tnOutputFile.close()
"""

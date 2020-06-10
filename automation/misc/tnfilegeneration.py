import requests
import pdftotext
import re


def is_number(s):
  try:
    int(s)
    return True
  except ValueError:
    return False

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

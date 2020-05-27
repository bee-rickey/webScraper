import deltaCalculator
import sys
import request
import json
import logging



logging.basicConfig(filename='covid19indiatracker_bot.log', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
stateName = ""
deltaCalculator = {}



def fetchData():
	print(stateName) 


def main():
	
	if len(sys.argv) > 1:
			stateName = sys.argv[1]

	deltaCalculator = DeltaCalculator()
	logging.info('Starting automation for state ' + stateName)
	fetchData()

if __name__ == '__main__':
	main()
	logging.info('Program end')

A scrapper for multiple covid state websites.

Used by www.covid19india.org admin teams. Not for general consumption :P

Usage:  
cd automation  
Comment lines in automation.meta that do not need to be run.    
  ./automation.py -- to run all for all states.  
  ./automation.py "state name" -- to get all details for that state.  
  ./automation.py "state name" "detailed" -- to get state details based on C, R, D categories.  
  ./automation.py "state name" "detailed" "pdf/ocr" -- currently supported only for PB.

OCR:  
  cd ocr  
  ./ocr.sh "Image Name" "State Name" "Starting String" "IsTranslationRequired"

**Automation support through URL fetch/scraping:**  
AP, OR, AS, TR, CH, PY, LA, GJ, MH, RJ (_RJ has stopped giving tables on their site_).

KA - district numbers and individual support (beta).

**Automation through OCR:**  
UP, RJ, PB, BR (Daily updates and bulletins)

**Automation support through pdf:**  
HR, PB, TN

**Future support:**  
KL (url), MP (pdf + ocr), HR (ocr), HP (ocr)

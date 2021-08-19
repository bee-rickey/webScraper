Currently there are three types of bulletins:

1. Images - AP, AR, BR, CT, JH, JK, HP, MH, MP, PB, RJ, TG, TN, UK, UP
2. PDFs - HR, KA, KL, PB, TN, WB
3. Dashboards - GJ, OR, PY, TR, Vaccines

For all those where ocr is supported (optical character recognition using google vision api), the command to run is:  
*./ocr.sh "fully qualified path to image" "State Name" "starting text, ending text" "True/False" "ocr/table/automation"*

Parameter description:
1. "fully qualified path to image": Example "./home/covid/mh.jpg" The path cannot be relative path but it should have the fully qualified path.  
2. "State Name": This is the state for which the image is being passed. Example: "Andhra Pradesh". 
3. "starting text, ending text": This is the starting text of an image which considered to be the begining of a bulletin. In case you want auto detection to kick in, use "auto,auto". In some of the cases, if the bulletin has a text above the table with district names, consider cropping the image to have only the table with district data.  
4. "True/False": This parameter is used in case you want to translate the district name (True: yes, please translate. False: No, do not translate). As of now this is applicable only to UP and BR bulletins.  
5. "ocr/table/automation": This is an option provided where in case you want to skip one or more of the steps (ocr, table creation or automation.py run), you can provide those steps in comma separated manner. Example: "ocr,automation" will skip both ocr step and the automation step. "ocr,table" will skip image reading and table creation, but will run automation.py step to compute the delta.


**How does the whole thing work?**




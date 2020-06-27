A scrapper for multiple covid state websites. Triedcatched's ghost!

Used by www.covid19india.org admin teams. Not for general consumption :P :D

Usage:  
cd automation  
Comment lines in automation.meta that do not need to be run.    
  ./automation.py -- to run all for all states.  
  ./automation.py "state name" -- to get all details for that state.  
  ./automation.py "state name" "detailed/full" -- to get state details based on C, R, D categories.  
  ./automation.py "state name" "detailed/full" "pdf/ocr" -- currently supported only for PB.

Getting details of KA bulletin:  
Place the bulletin in .tmp folder as ka.pdf.  
Run `./kaconfirmed.py`. This gives the output in kaconfirmed.csv file.  
Run `./karecoveries.py`. This assumes the recovery table to be the 4th page (can make this user input, but holding off for now). Gives the output in karecoveries.csv file.

OCR:  
  cd ocr  
  ./ocr.sh "Image Name" "State Name" "Starting String" "IsTranslationRequired" "ocr,table,automation"

The last argument tells which of the steps to skip. This is used for images that need manual intervention.

**Automation support through URL fetch/scraping:**  
AP, AS, CH, KL, LA, GJ, MH, MP, OR, PY, TR, RJ (_RJ has stopped giving tables on their site_).

KA - district numbers and individual support (beta).

**Automation through OCR:**  
BR, MP, PB, RJ, UP 

**Automation support through pdf:**  
HR, PB, TN, WB

**Future support:**  
MP (pdf), HR (ocr), HP (ocr)

**Complete description of OCR methodology and debugging**

ocr.sh has three parts to it -

1. Google vision API call:  
Arguments: "ImageName"  
Output: bounds.txt  
Description: This corresponds to the line `python3 ocr_vision.py $1 > bounds.txt` in ocr.sh. This is used to call google vision api and get the output in a file.  
The output has the following format:  
`<text>|lower left x,y|lower right x,y|upper right x,y|upper left x,y`  
This output is present in the bounds.txt file. The file also contains the texts with a json structure which is not used currently.

2. googlevision.py script:  
Arguments: ocrconfig.meta "Image"  
Output: output.txt  
Description: This corresponds to the line `python3 googlevision.py ocrconfig.meta $1`. The task of this script is to get a csv out of the bounds.txt file.  

The configuration file ocrconfig.meta file has some configurations that control texts to be considered, translations and error for row and column calculations.

	startingText:startingtext  
	enableTranslation:translationvalue  
	translationFile:statename_districts.meta  
	yInterval:0  
	xInterval:0  


a. First step is to build a cell which has the following attributes:  
	a.1) Text  
	a.2) Center coordinates of the text: x,y  
	a.3) Lower left x, lower left y  
	a.4) Height of the text (calculated using lower left and upper left coordinates). 
	a.5) Width of the text (calculated using lower left and lower right coordinates). Height and width are used for displaying the recognized text a debug solution.   
	a.6) Column number.  
	a.7) Row number.  

b. Next, if there is a starting text provided, then we discard all those objects whose y is less than that of the y of StartingText and whose x is less than that of the x of StartingText. This allows for a better accuracy when we try to recreate the table structure. If there is no StartingText provided, this step is skipped.

c. Once we have filtered out unwanted texts, then next step is to figure out the structure. The logic goes like this:  
c.1) Take the array of cells representing individual texts.  
c.2) Loop through each of these cells. In each step, figure out all the other cells that have same x coordinate. These are the ones that lie in the same column. Hence assign these the same column number as the current cell being considered. Ignore all cells that are already assigned a column value.  
c.3) Figure out all the cells that have same y coordinate. These are the ones that lie on the same row. Assign these cells the same row value as the current cell being considered. Ignore all cells that have already their row value set.  

This step will assign all texts found on the same line with the same row number and all texts found on the same column with the same column number. However, this step is a bit tricky. The reason is, the x,y of the center of the texts need not align perfectly with others in the same column due to their width. This works fine if all are center aligned. If the texts are right or left aligned, there's a possiblity of values in the same column not matching up on their x coordinates.  

To remedy this (or atleast to provide a bit of flexibility), there's a consideration of xInterval that's provided. This value is used to provide a range on the x value of texts to decide if texts need to be considered to be on the same column. i.e, if `T1.x + xInterval <= T2.x <= T1.x - xInterval` then T2 is assigned the column value of T1.

Note: The above method of finding columns is debatable. Still needs refinement.

c.4) The penultimate step of this script is to provide an output. This is done by first sorting the row values based on x value. This makes sure that their order is maintained. Then, there's a loop over the individual row values to decide if there needs to be some merges that need to happen. This is done to handle scenarios where certain columns have texts separated by spaces. The column numbers are also printed per row seperated from the main values by a pipe. This is done for any debugging that the consumer might wish to do.

c.5) Once done, if translations is enabled, then, we consider the first column and do a lookup on statename_districts.meta file to convert the vernacular text into English.

3. Run automation.py to figure out deltas.  
Arguments: "StateName" "detailed" "ocr"  
Output: Gives a delta for each category and district for the state name mentioned.  
Description: This uses the output.txt file to decide on what the delta will be for the given state.  



**FAQ**

1. I want to just get data out of the image. I do not want to translate or figure out delta. What do I do?  
A: Run ./ocr.sh "Image" "" "" "False". Then the output should be present in output.txt file.

2. I want to run the ocr, translate district names, but I do not want a delta. What do I do?  
A: Open automation.meta file, add a # in the beginning of the line corresponding to the state. Run ./ocr.sh "Image" "StateName" "" "True". The output should be present in output.txt file.

3. When I run ocr script, I see some texts saying "Failed to find lookup for xyz". Why is this?  
A: This happens when the TranslationValue is set to True and the code tries to find an entry corresponding to it in the stateCode_translation.meta file and fails to find one.

4. I get an ArrayIndexOutOfBounds error.  
A: This happens when the columns mismatch due to either column assignment being wrong or google vision api not being able to detect the text. The best bet here is to open output.txt and figure out what is wrong. Next, comment the line `python3 ocr_vision.py $1 > bounds.txt`. If you want to remove that district data completely, comment `cp output.txt ../.tmp/$stateCode.txt` and rerun the ocr command.

5. I see some messages that say that some corrections were tried. What does this mean?  
A: For certain states like UP, PB the automation code tries to add a default -999 entry if it finds some columns missing. This message pertains to that. Caution needs to be exercised when it comes to these entries.

6. When I open output.txt file, I see that certain rows have non translated texts. What do I do?  
A: This is mostly due to the xInterval being wrong. The default value of xInterval is the max text width found in the image. You can change this by altering ocrconfig.meta.orig file. Rerun the ocr script after this. A higher value of xInterval means that multiple columns might get clubbed into one. A lower value means that there'll be a stricter bifurcation of columns. 

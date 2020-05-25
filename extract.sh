today=`date +"%d_%b_%Y"`
mkdir $today
git add --all
curl https://covid19.nagaland.gov.in/ > x.html
python3 extract.py
git commit -m "Folder creation"

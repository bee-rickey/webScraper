today=`date +"%d_%b_%Y"`
mkdir data/$today
curl https://covid19.nagaland.gov.in/ > x.html
python3 extract.py $today
#git pull
#git add --all
#git commit -m "Folder creation"
#git push --all

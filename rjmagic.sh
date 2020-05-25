curl https://api.covid19india.org/csv/latest/district_wise.csv | grep "Rajasthan" > rj.csv

while read line 
do
	district=`echo $line | awk -F, '{print $2}'`
	positives=`echo $line | awk -F, '{print $5}'`
	recovery=`echo $line | awk -F, '{print $6}'`

    districtLine=`grep $district rj.csv`
    siteConfirmed=`echo $districtLine | awk -F, '{print $6}'`
    siteRecovery=`echo $districtLine | awk -F, '{print $8}'`
	
	echo "$district, $((positives - siteConfirmed)), $((recovery - siteRecovery))"

done < data/24_may_2020/Rajasthan.csv

curl https://api.covid19india.org/csv/latest/district_wise.csv | grep "Rajasthan" > rj.csv
noOfLines=`wc -l < data/25_may_2020/Rajasthan.csv`
LinesToRead=$(( noOfLines - 1 ))
tail -n $LinesToRead data/25_may_2020/Rajasthan.csv > .rjsite.csv
LinesToRead=$(( noOfLines - 7 ))

head -n $LinesToRead .rjsite.csv > rjsite.csv


while read line 
do
	district=`echo $line | awk -F, '{print $2}'`
	positives=`echo $line | awk -F, '{print $5}'`
	recovery=`echo $line | awk -F, '{print $6}'`

	if [ "$district" == "S. Madhopur" ]
	then
		district="Sawai Madhopur"
	fi

    districtLine=`grep "$district" rj.csv`
    siteConfirmed=`echo $districtLine | awk -F, '{print $6}'`
    siteRecovery=`echo $districtLine | awk -F, '{print $8}'`
	
	echo "$district, $((positives - siteConfirmed)), $((recovery - siteRecovery))"

done < rjsite.csv

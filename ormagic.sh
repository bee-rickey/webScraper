#!/usr/bin/env bash
curl -s https://health.odisha.gov.in/js/distDtls.js | grep -i 'District_id' | sed 's/"//g' | sed 's/,/:/g'| cut -d':' -f4,8,12,14,18,22 |sed 's/:/,/g' > orsite.csv
curl -s https://api.covid19india.org/csv/latest/district_wise.csv | grep 'Odisha' > current_or.csv 


declare -A districtMappings
districtMappings['Sonepur']='Subarnapur'
districtMappings['Khurdha']='Khordha'
districtMappings['Sundergarh']='Sundargarh'
districtMappings['Keonjhar']='Kendujhar'
districtMappings['Baragarh']='Bargarh'
districtMappings['Nawarangpur']='Nabarangapur'



while read line
do
	read -r district confirmed recovered deceased <<< $(echo $line | awk -F, '{print $1, $2, $3, $4}')

	if [ ! -z "${districtMappings[$district]}" ]
	then
    	district=${districtMappings[$district]}
	fi
	
	row=`grep -i "$district" current_or.csv`
	read -r currentDistrict currentConfirmed currentRecovered currentDeceased <<< $(echo $row | awk -F, '{print $5, $6, $8, $9}')

	deltaConfirmed=$((confirmed - currentConfirmed))
	deltaRecovered=$((recovered - currentRecovered))
	deltaDeceased=$((deceased - currentDeceased))

	echo "$district, $deltaConfirmed, $deltaRecovered, $deltaDeceased"
	

done < orsite.csv

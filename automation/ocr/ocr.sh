customiseMetaConfig() {
  stateCode=$( echo $1 )
  replacementLine=$( echo $2 )
  sedString=$( echo $3 )
  parameterStateCode=$( echo $3 | cut -d':' -f1 )
  parametersToReplace=$( echo $3 | cut -d':' -f2 )
  if [ "$stateCode" = "$parameterStateCode" ]
  then
    for param in $(echo $parametersToReplace | sed "s/,/ /g")  
    do
      parameterToReplace=$( echo $param | cut -d'=' -f1 )
      value=$( echo $param | cut -d'=' -f2 )
      replacementSubString=$( echo "$replacementSubString;s/\\\$$parameterToReplace/$value/g" )
    done
  fi
  echo $replacementLine | sed "$replacementSubString"
}



if (( $# != 4 && $# != 5 ))
then
  echo "Usage: ./ocr.sh <Image Name> <State Name> [Starting String] <IsTranslationRequired>"
  exit
fi

format="ocr"

skipOcr=0
skipTable=0
skipAutomation=0
individualRecords=0

if (( $# == 5 ))
then
  for i in $(echo $5 | sed "s/,/ /g")
  do
    option=`echo $i |awk '{print tolower($0)}'`

    case $option in
      "all")
        ;;
      "ocr")
        skipOcr=1
        echo "**** Skipping OCR Generation ****"
        ;;
      "table")
        echo "**** Skipping CSV Generation ****"
        skipTable=1
        ;;
      "automation")
        echo "**** Skipping Automation ****"
        skipAutomation=1
        ;;
      "ocr,table")
        echo "**** Skipping OCR, CSV Generation ****"
        skipOcr=1
        skipTable=1
        ;;
      "individual")
        individualRecords=1
        ;;
      "f1")
        echo "**** Using format type 1 for UP ****"
        format="ocr1"
        ;;
      "f2")
        echo "**** Using format type 2 for UP ****"
        format="ocr2"
        ;;
    esac
  done
fi

stateCode=""
case $2 in
  "Bihar")
    stateCode="br"
    ;;
  "Uttar Pradesh")
    stateCode="up"
    ;;
  "Madhya Pradesh")
    stateCode="mp"
    ;;
  "Jharkhand")
    stateCode="jh"
    ;;
  "Rajasthan")
    stateCode="rj"
    ;;
  "Punjab")
    stateCode="pb"
    ;;
  "Jammu and Kashmir")
    stateCode="jk"
    ;;
  "Haryana")
    stateCode="hr"
    ;;
  "Andhra Pradesh")
    stateCode="ap"
    ;;
  "Maharashtra")
    stateCode="mh"
    ;;
  "Himachal Pradesh")
    stateCode="hp"
    ;;
  "Chhattisgarh")
    stateCode="ct"
    ;;
  "Uttarakhand")
    stateCode="ut"
    ;;
  "Arunachal Pradesh")
    stateCode="ar"
    ;;
  "Gujarat")
    stateCode="gj"
    ;;
  "Tamil Nadu")
    stateCode="tn"
    ;;
  "Nagaland")
    stateCode="nl"
    ;;
  "Telangana")
    stateCode="tg"
    ;;
  "Karnataka")
    stateCode="ka"
    ;;
  "Sikkim")
    stateCode="sk"
    ;;
  "Mizoram")
    stateCode="mz"
    ;;
  "Meghalaya")
    stateCode="ml"
    ;;
  "Kerala")
    stateCode="kl"
    ;;
  "Assam")
    stateCode="as"
    ;;
    
  *)
    stateCode="invalid"
esac

echo -e "\n********************* If you want to see the ocr data, cat output.txt *********************\n"

if (( $skipOcr != 1 ))
then
  echo -e "\n******** Calling google vision api *******"
  python3 ocr_vision.py $1 > bounds.txt
fi

if (( $skipTable != 1 ))
then
  replacementLine="s/@@statename@@/\$stateCode/g;s/@@yInterval@@/\$yInterval/g;s/@@xInterval@@/\$xInterval/g;s/@@houghTransform@@/\$houghTransform/g;s/@@enableTranslation@@/\$enableTranslation/g;s/@@startingText@@/\$startingText/g;s/@@configMinLineLength@@/\$configMinLineLength/g;"

  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "hp:houghTransform=False,yInterval=5" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "br:houghTransform=False" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "mp:houghTransform=False" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "ap:configMinLineLength=300" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "tn:configMinLineLength=500" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "tg:enableTranslation=True" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "mz:houghTransform=False" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "ml:configMinLineLength=250" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "ut:houghTransform=False" )
  replacementLine=$( customiseMetaConfig $stateCode $replacementLine "nl:configMinLineLength=250" )

  configMinLineLength=400
  enableTranslation=`echo $4`
  startingText=`echo $3`
  houghTransform="True"
  yInterval=0
  xInterval=0

  finalReplacementString=$( echo $replacementLine | sed "s/\$stateCode/$stateCode/g; s/\$yInterval/$yInterval/g; s/\$xInterval/$xInterval/g; s/\$houghTransform/$houghTransform/g; s/\$enableTranslation/$enableTranslation/g; s/\$startingText/$startingText/g; s/\$configMinLineLength/$configMinLineLength/g" )

  echo $finalReplacementString

  sed "$finalReplacementString" ocrconfig.meta.orig > ocrconfig.meta

  echo -e "\n******** Using ocrconfig.meta, change ocrconfig.meta.orig for x and y intervals ******* "
  cat ocrconfig.meta
  echo -e "******** ++++++++ *******"
  python3 googlevision.py ocrconfig.meta $1
fi

cp output.txt ../.tmp/$stateCode.txt

if (( $skipAutomation != 1 && $individualRecords != 1 ))
then
  cd ..
  echo -e "\n******** Calling automation.py for $2  ******* "
  python3 ./automation.py "$2" "full" $format
fi

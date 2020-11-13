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
  lineLength=400
  translationValue=`echo $4`
  if [ "$stateCode" = "tn" ]
  then
    lineLength=500
  fi
  if [ "$stateCode" = "tg" ]
  then
    translationValue="True"
  fi


	yInterval=0
	if [ "$stateCode" = "ml" ]
	then
  	yInterval=10
	fi

  if [ "$stateCode" = "mz" -o "$stateCode" = "nl" -o "$stateCode" = "hp" ]
  then
    sed "s/@@yinterval@@/$yInterval/g; s/@@houghTransform@@/False/g; s/@@statename@@/$stateCode/g; s/@@startingtext@@/$3/g; s/@@translationvalue@@/$translationValue/g; s/@@linelength@@/$lineLength/g;" ocrconfig.meta.orig > ocrconfig.meta
  else
    sed "s/@@yinterval@@/$yInterval/g; s/@@houghTransform@@/True/g; s/@@statename@@/$stateCode/g; s/@@startingtext@@/$3/g; s/@@translationvalue@@/$translationValue/g; s/@@linelength@@/$lineLength/g;" ocrconfig.meta.orig > ocrconfig.meta
  fi

  if [ "$stateCode" = "mz" -o "$stateCode" = "nl" -o "$stateCode" = "hp" ]
  then
    sed "s/@@yinterval@@/$yInterval/g; s/@@houghTransform@@/False/g; s/@@statename@@/$stateCode/g; s/@@startingtext@@/$3/g; s/@@translationvalue@@/$translationValue/g; s/@@linelength@@/$lineLength/g;" ocrconfig.meta.orig > ocrconfig.meta
	fi


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

if (( $individualRecords == 1 ))
then
  cd ..
  case $2 in
    "Bihar")
      python3 ./biharIndividual.py
      ;;
    *)
      echo "No custom script found"
      ;;
  esac
fi

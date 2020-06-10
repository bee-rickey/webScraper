python3 ocr_vision.py $1 > bounds.txt

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
	*)
		stateCode="invalid"
esac

sed "s/@@statename@@/$stateCode/g; s/@@startingtext@@/$3/g; s/@@translationvalue@@/$4/g" ocrconfig.meta.orig > ocrconfig.meta
python3 googlevision.py ocrconfig.meta
cp output.txt ../$stateCode.txt
cd ..
./automation.py "$2" "detailed"

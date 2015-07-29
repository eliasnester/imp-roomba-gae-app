#!/bin/bash
source config.ini
echo $APP
echo $WEB_CLIENT_ID

TMP_FILE="temp"

# patch app.yaml with application name from config.ini
sed "s/YOUR_APP_NAME/$APP/g" app.yaml > TMP_FILE
mv TMP_FILE app.yaml

# patch endpoints API and javascript to use your API key
files=("roomba.py" "static/js/roomba.js")
for f in "${files[@]}"
do
    echo $f
    sed "s/YOUR_WEB_CLIENT_ID/$WEB_CLIENT_ID/g" $f > TMP_FILE
    mv TMP_FILE $f
    #cat $f | grep $WEB_CLIENT_ID > ttt
done
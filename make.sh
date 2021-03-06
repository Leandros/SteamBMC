#!/bin/bash
# Creates a Zip file for the addon, with correct naming and versioning.

DEBUG=0
DIR=${PWD##*/}

read_dom () {
    local IFS=\>
    read -d \< ENTITY CONTENT
}


while getopts “d” OPTION
do
    case $OPTION in
        d)
          DEBUG=1
          ;;
    esac
done

while read_dom; do
    if [[ $ENTITY == addon* ]]; then
        LINE="$ENTITY"
        break
    fi
done < addon.xml

SUBSTRING_ID=`echo $LINE | cut -d' ' -f 2`
SUBSTRING_VERSION=`echo $LINE | cut -d' ' -f 4`
ID=`echo $SUBSTRING_ID | cut -c5- | rev | cut -c2- | rev`
VERSION=`echo $SUBSTRING_VERSION | cut -c10- | rev | cut -c2- | rev`

if [[ $DEBUG == 1 ]]; then
    FILE=`find * -name "$ID-$VERSION*"`
    if [[ ${#FILE} > 0 ]]; then
        NUM=`echo "$FILE" | grep -o "-" | wc -l`
        if [[ $NUM -gt 1 ]]; then
            RNUM=`echo $FILE | cut -d'-' -f 3 | rev | cut -c5- | rev`
            rm $ID-$VERSION-$RNUM.zip >/dev/null 2>&1
            rm ~/___xbmc/$ID-$VERSION-$RNUM.zip >/dev/null 2>&1
            RNUM=`expr $RNUM + 1`
        else
            RNUM=1
        fi
    else
        RNUM=1
    fi
fi

rm $ID-$VESION.zip >/dev/null 2>&1

mkdir $ID
rsync -ra --exclude=$ID --exclude='.DS_STORE' --exclude='.*' --exclude='make.sh' --exclude='*.zip' . $ID
if [[ $DEBUG == 1 ]]; then
    zip -r -q $ID-$VERSION-$RNUM.zip $ID
    cp $ID-$VERSION-$RNUM.zip ~/___xbmc/$ID-$VERSION-$RNUM.zip
    echo "Zip file created, it's called '$ID-$VERSION-$RNUM.zip'"
else
    zip -r -q $ID-$VERSION.zip $ID
    echo "Zip file created, it's called '$ID-$VERSION.zip'"
fi
rm -rf $ID

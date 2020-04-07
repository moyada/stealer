#!/bin/sh

workdir=$(cd $(dirname $0); pwd)
file=$workdir'/'$1

if [ ! -f "$file" ]; then
 echo 'error: file not exist!'
 exit
fi

echo 'old md5 >>>' $(md5 -q $file)

echo 0 >> $file
echo 'new md5 >>>' $(md5 -q $file)
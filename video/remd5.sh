#!/bin/sh


f=${1:0:1}

if [ "$f" = "/" ]; then
  file=$1
else
  workdir=$(cd $(dirname $0); pwd)
  file=$workdir'/'$1
fi

if [ ! -f "$file" ]; then
 echo 'error: '$file' file not exist!'
 exit
fi

echo 'old md5 >>>' $(md5 -q $file)

echo 0 >> $file
echo 'new md5 >>>' $(md5 -q $file)
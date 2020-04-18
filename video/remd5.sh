#!/bin/sh

command=$1
#截取第一位字符
f=${2:0:1}

if [ "$f" = "/" ]; then
  file=$2
else
  workdir=$(cd $(dirname $0); pwd)
  file=$workdir'/'$2
fi

if [ ! -f "$file" ]; then
 echo 'error: '$file' file not exist!'
 exit
fi

echo 'old md5 >>>' $($command $file)

echo 0 >> $file
echo 'new md5 >>>' $($command $file)
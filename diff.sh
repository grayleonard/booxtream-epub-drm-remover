#!/bin/bash
if [ $2 = "" ]
	then echo 'md5sum.sh file1 file2'
	exit
fi

# make temp dirs to extract to
mkdir .1 
mkdir .2

unzip "$1" -d .1/ > /dev/null 2>&1
unzip "$2" -d .2/ > /dev/null 2>&1

for file in $(find .1 -type f);
do
	comp=$(echo "$file" | sed 's/1/2/')
	echo "Comparing files $comp" "$file"; 
	diff "$comp" "$file";
done

rm -rf .1
rm -rf .2

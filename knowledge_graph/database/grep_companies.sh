#!/bin/bash
input="listed_company.txt"
while IFS= read -r var
do
    grep "$var" /home/weiwu/share/deep_learning/data/zhwiki/baike_triples.txt
done < "$input"

#!/bin/zsh
for number in {0..4}
do
    workon graph
    python main.py $number &
    echo "$number "
done
exit 0

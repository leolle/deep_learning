#!/bin/bash
if [ -z "$*" ]
then
    git commit -m "update notes"
else
    git commit -m "$*"
fi

grep -inR "$@" . --include \*.py --exclude-dir=basic

#!/bin/bash
if [ -z "$*" ]
then
    grep -inR "$@" . --include \*.py --exclude-dir=basic
else
    grep -inR "$@" "$*" --include \*.py --exclude-dir=basic
fi

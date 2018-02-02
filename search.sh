#!/bin/bash
grep -inR "$@" . --include \*.py --exclude-dir=basic

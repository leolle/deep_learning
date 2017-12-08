#!/bin/bash
grep -inR "$@" . --include \*.py

#!/bin/sh
N=1000
if [ "$(./randall "$N" | wc -c)" = "$N" ]; then
    exit 0 # Success!
else
    exit 1 # Fail :(
fi

#!/bin/sh -l

echo "Checking website $1. Verbose mode $1"
time=$(date)
echo ::set-output name=time::$time
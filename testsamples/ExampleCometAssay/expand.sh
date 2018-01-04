#!/bin/sh

for idx in $(seq 7 9); do
  cp images/CometTails.tif "images/NewCometTails.tif"
  cp images/NoTails.tif    "images/NewNoTails.tif"
done

echo ".tif"

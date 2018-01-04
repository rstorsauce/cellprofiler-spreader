#!/bin/sh

for idx in $(seq 1 3); do
  cp images/AS_09125_050116030001_D03f00d0.tif "images/AS_09125_050116030001_D03f0${idx}d0.tif"
  cp images/AS_09125_050116030001_D03f00d1.tif "images/AS_09125_050116030001_D03f0${idx}d1.tif"
  cp images/AS_09125_050116030001_D03f00d2.tif "images/AS_09125_050116030001_D03f0${idx}d2.tif"
done

echo "d1.tif"

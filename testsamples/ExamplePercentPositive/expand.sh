#!/bin/sh

for idx in $(seq 2 4); do
  cp images/AS_09125_050116030001_D03f00d0.tif "images/AS_09125_05011603000${idx}_D03f00d0.tif"
  cp images/AS_09125_050116030001_D03f00d1.tif "images/AS_09125_05011603000${idx}_D03f00d1.tif"
done

echo "D03f00d0.tif"

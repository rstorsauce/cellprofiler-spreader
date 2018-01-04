#!/bin/sh

for idx in $(seq 2 4); do
  cp images/Clones1.JPG "images/Clones$idx.JPG"
done

echo ".JPG"

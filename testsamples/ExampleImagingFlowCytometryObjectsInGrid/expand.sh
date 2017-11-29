#/bin/sh

for idx in $(seq 2 4); do
  cp images/1-Ch1_1.tif "images/$idx-Ch1_1.tif"
  cp images/1-Ch1_2.tif "images/$idx-Ch1_2.tif"
  cp images/1-Ch6_1.tif "images/$idx-Ch6_1.tif"
  cp images/1-Ch6_2.tif "images/$idx-Ch6_2.tif"
  cp images/1-Ch7_1.tif "images/$idx-Ch7_1.tif"
  cp images/1-Ch7_2.tif "images/$idx-Ch7_2.tif"
done

echo "-Ch1_1.jpg"

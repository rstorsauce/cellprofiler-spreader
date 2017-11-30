#/bin/sh

for idx in $(seq 3 5); do
  cp images/1-162hrh2ax2.tif "images/1-16${idx}hrh2ax2.tif"
  cp images/1-162hrhoe2.tif  "images/1-16${idx}hrhoe2.tif"
done

echo "h2ax2.tif"

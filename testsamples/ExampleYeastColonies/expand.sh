#/bin/sh

for idx in $(seq 7 9); do
  cp images/6-1.jpg "images/$idx-1.jpg"
  cp images/6-1.png "images/$idx-1.png"
done

echo "-1.jpg"

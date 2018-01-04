#!/bin/sh

for idx in seq 17 19; do
  cp "images/101210OranePlt1_C16_w1_[9AA4D9EA-18E4-4354-8C7D-0202029A8048].tif" "images/101210OranePlt1_C${idx}_w1_[E3E9B145-D9B7-49E1-8159-496F065708F8].tif"
  cp "images/101210OranePlt1_C16_w2_[EFB0F53A-F40F-46D8-A61A-51C2BE61E460].tif" "images/101210OranePlt1_C${idx}_w2_[EFB0F53A-F40F-46D8-A61A-51C2BE61E460].tif"
  cp "images/101210OranePlt1_C16_w3_[E3E9B145-D9B7-49E1-8159-496F065708F7].tif" "images/101210OranePlt1_C${idx}_w3_[E3E9B145-D9B7-49E1-8159-496F065708F7].tif"
done

echo "r/w3_(.*).tif/"

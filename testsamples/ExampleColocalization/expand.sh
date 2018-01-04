#!/bin/sh

for idx in $(seq 2 4); do
  cp images/0_1_N_G.png "images/0_${idx}_N_G.png"
  cp images/0_1_N_R.png "images/0_${idx}_N_R.png"
done

echo "_N_G.png"

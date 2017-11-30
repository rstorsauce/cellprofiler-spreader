#/bin/sh

for idx in $(seq 6 8); do
  cp images/DMSO_B5_t0.JPG  "images/DMSO_B${idx}_t0.JPG"
  cp images/DMSO_B5_t24.JPG "images/DMSO_B${idx}_t24.JPG"
done

echo "_t0.JPG"

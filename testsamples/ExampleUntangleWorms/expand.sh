#!/bin/sh
for idx in $(seq 2 3); do
  cp images/1649_1109_0003_Amp5-1_B_20070424_C01_w1_10E01AFB-34C4-416E-A9D3-51B90AB53728.tif "images/1649_1109_0003_Amp5-1_B_20070424_C0${idx}_w1_10E01AFB-34C4-416E-A9D3-51B90AB53728.tif"
  cp images/1649_1109_0003_Amp5-1_B_20070424_C01_w2_CB2F18CD-EDF0-4BCD-98CF-3A07E5A582FF.tif "images/1649_1109_0003_Amp5-1_B_20070424_C0${idx}_w2_CB2F18CD-EDF0-4BCD-98CF-3A07E5A582FF.tif"
done

echo "r/w1_(.*).tif/"

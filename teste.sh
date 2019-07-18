#!/bin/bash -x

mkdir -p /home/ubuntu/poc-face-detect-server/uploads/files
cp /tmp/files.zip /home/ubuntu/poc-face-detect-server/uploads/
python3 /home/ubuntu/poc-face-detect-server/faceGenderAge.py  


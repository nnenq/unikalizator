#!/bin/bash
# usage: bash /root/docengine/full.sh NAME   (run inside project dir)
set -e
NAME=$1; ENG=/root/docengine
N=$(python3 $ENG/dk.py info | sed -E 's/.* ([0-9]+) frames.*/\1/')
mkdir -p chunks
seq 0 $(( (N - 1) / 1500 )) | xargs -P 4 -I{} sh -c "i={}; f=chunks/c\$(printf %03d \$i).mp4; [ -s \$f ] || { python3 $ENG/dk.py range \$((i*1500)) \$(( (i+1)*1500 < $N ? (i+1)*1500 : $N )) \$f.tmp.mp4 && mv \$f.tmp.mp4 \$f; echo chunk \$i done; }"
ls chunks/c*.mp4 | sed "s#^#file '$PWD/#;s#\$#'#" > parts.txt
ffmpeg -v error -y -f concat -safe 0 -i parts.txt -c copy video.mp4
python3 $ENG/audio.py
ffmpeg -v error -y -i video.mp4 -i final.wav -map 0:v -map 1:a -c:v libx264 -preset medium -b:v 3200k -pass 1 -passlogfile p2 -an -f null /dev/null
ffmpeg -v error -y -i video.mp4 -i final.wav -map 0:v -map 1:a -c:v libx264 -preset medium -b:v 3200k -pass 2 -passlogfile p2 -c:a aac -b:a 192k -shortest -movflags +faststart $NAME.mp4
ls -la $NAME.mp4; ffprobe -v error -show_entries format=duration -of csv=p=0 $NAME.mp4
ffmpeg -hide_banner -i $NAME.mp4 -vf "freezedetect=n=-60dB:d=2.5,blackdetect=d=0.7" -af "ebur128=peak=true" -f null - 2>&1 | grep -E "freeze_start|black_start|^\s+I:|^\s+Peak:" || true
echo ALLDONE

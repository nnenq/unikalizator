#!/bin/bash
# usage: sheet.sh OUT.jpg [cols]  (tiles stills/*.png with labels)
OUT=$1; C=${2:-5}; cd stills; L=$(ls *.png); n=$(echo "$L" | wc -l)
ffmpeg -v error -y $(echo "$L" | sed 's/^/-i /' | tr '\n' ' ') -filter_complex "$(k=0; for f in $L; do printf '[%d]scale=384:216,drawtext=text=%s:fontcolor=yellow:fontsize=16:x=4:y=4[v%d];' $k ${f%.png} $k; k=$((k+1)); done; for k in $(seq 0 $((n-1))); do printf '[v%d]' $k; done; printf 'xstack=inputs=%d:fill=black:layout=' $n; for k in $(seq 0 $((n-1))); do printf '%s_%s|' $(( (k%C)*384 )) $(( (k/C)*216 )); done | sed 's/|$//')" -frames:v 1 $OUT

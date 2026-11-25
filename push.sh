#!/bin/bash
# usage: bash /root/docengine/push.sh NAME  (in project dir; pushes NAME/{mp4 parts, srt, txt} to branches videos + video-NAME)
set -e
NAME=$1; P=$PWD; R=/home/user/unikalizator; S=$P/up
rm -rf "${S:?}"; mkdir -p $S; cd $S
split -b 90M -d -a 2 $P/$NAME.mp4 $NAME.mp4.part
PT=$(ls $NAME.mp4.part* | tr '\n' '+' | sed 's/+$//')
printf '@echo off\r\ncd /d "%%~dp0"\r\ncopy /b %s %s.mp4\r\necho Done: %s.mp4\r\npause\r\n' "$PT" "$NAME" "$NAME" > JOIN_VIDEO.bat
cp $P/${NAME}_en.srt $P/${NAME}_youtube.txt .
cd $R
for i in 1 2 3 4; do git fetch -q origin videos && break; sleep $((i*3)); done
export GIT_INDEX_FILE=$P/idx; rm -f $GIT_INDEX_FILE
git read-tree origin/videos
PARENT=$(git rev-parse origin/videos)
for f in ${NAME}_youtube.txt ${NAME}_en.srt $(ls $S/$NAME.mp4.part* | xargs -n1 basename) JOIN_VIDEO.bat; do
  H=$(git hash-object -w $S/$f)
  git update-index --add --cacheinfo 100644,$H,$NAME/$f
  T=$(git write-tree)
  C=$(git commit-tree $T -p $PARENT -m "Add $NAME/$f" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01SNgKBNtipmcgFHHPuePVK6")
  for i in 1 2 3 4; do git push -q origin $C:refs/heads/videos 2>&1 | grep -v acknowledg || true; git ls-remote origin refs/heads/videos | grep -q $C && break; sleep $((i*4)); done
  PARENT=$C
done
VT=$(git rev-parse $PARENT:$NAME)
VC=$(git commit-tree $VT -m "Video: $NAME" -m "Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>" -m "Claude-Session: https://claude.ai/code/session_01SNgKBNtipmcgFHHPuePVK6")
for i in 1 2 3 4; do git push -q origin $VC:refs/heads/video-$NAME 2>&1 | grep -v acknowledg || true; git ls-remote origin refs/heads/video-$NAME | grep -q $VC && break; sleep $((i*4)); done
git ls-remote origin refs/heads/videos refs/heads/video-$NAME
cd $S && cat $NAME.mp4.part* | md5sum && md5sum $P/$NAME.mp4

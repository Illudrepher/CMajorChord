#!/usr/bin/env bash
set -e
SONG_SOURCE="$1"
ID_FROM_SOURCE="$2"
MP3_PATH="$3"
MP3_NAME="$4"
 
cd /app/mir
OUT_DIR_NAME="${SONG_SOURCE}-${ID_FROM_SOURCE}"
cp "$MP3_PATH" "./${OUT_DIR_NAME}.mp3"
spleeter separate -p spleeter:4stems -o output "${OUT_DIR_NAME}.mp3"
python3 mir.py "output/${OUT_DIR_NAME}"
rm "./${OUT_DIR_NAME}.mp3"
echo "analysis ${OUT_DIR_NAME} is now down on the backend." 

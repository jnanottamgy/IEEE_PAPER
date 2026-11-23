#!/bin/bash
# Build both PDFs: review (single column, IEEE draft) and camera-ready (two column).
set -e
cd "$(dirname "$0")"
run() { pdflatex -interaction=nonstopmode -halt-on-error -jobname="$1" "$2" > /dev/null; }
for job in review camera; do
  if [ $job = camera ]; then src='\def\cameraready{1}\input{main}'; else src='\input{main}'; fi
  run "main_$job" "$src"; bibtex "main_$job" > /dev/null; run "main_$job" "$src"; run "main_$job" "$src"
  echo "main_$job.pdf: $(pdfinfo main_$job.pdf | awk '/Pages/{print $2}') pages"
done

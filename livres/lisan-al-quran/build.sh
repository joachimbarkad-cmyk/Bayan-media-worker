#!/bin/sh
# Construit le livre : HTML, puis PDF en deux passes (numéros de page du sommaire).
set -e
cd "$(dirname "$0")"
[ -f cache/quran-morphology.txt ] || ./fetch_data.sh
python3 src/build.py
node src/render.cjs src/livre.html build/pass1.pdf
python3 src/pages.py build/pass1.pdf build/pages.json
python3 src/build.py --pages build/pages.json
node src/render.cjs src/livre.html Lisan-al-Quran.pdf
python3 src/pages.py Lisan-al-Quran.pdf build/pages-final.json
cmp -s build/pages.json build/pages-final.json || echo "ATTENTION : pagination instable, relancer build.sh"
echo "livre : $(pwd)/Lisan-al-Quran.pdf"

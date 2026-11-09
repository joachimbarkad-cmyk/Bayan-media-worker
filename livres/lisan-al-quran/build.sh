#!/bin/sh
# Construit le livre : HTML, puis PDF en deux passes (numéros de page du sommaire).
set -e
cd "$(dirname "$0")"
[ -f cache/quran-morphology.txt ] || ./fetch_data.sh
python3 src/build.py
node src/render.cjs src/livre.html build/pass1.pdf --tagged
python3 src/pages.py build/pass1.pdf build/pages.json
python3 src/build.py --pages build/pages.json
node src/render.cjs src/livre.html Lisan-al-Quran.pdf
python3 src/verif_pages.py Lisan-al-Quran.pdf build/pages.json
echo "livre : $(pwd)/Lisan-al-Quran.pdf"

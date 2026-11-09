#!/bin/sh
# Télécharge les sources du texte coranique et les polices dans cache/.
set -e
cd "$(dirname "$0")"
mkdir -p cache/fonts
curl -sSf -o cache/quran-morphology.txt https://raw.githubusercontent.com/mustafa0x/quran-morphology/master/quran-morphology.txt
TMP=$(mktemp -d)
(cd "$TMP" && npm pack --silent quran-json@3.1.2 >/dev/null && tar xzf quran-json-3.1.2.tgz)
cp "$TMP/package/dist/quran.json" cache/quranenc-uthmani.json
cp "$TMP/package/dist/quran_fr.json" cache/quranenc-fr.json
rm -rf "$TMP"
B=https://raw.githubusercontent.com/google/fonts/main/ofl
for p in amiriquran/AmiriQuran-Regular.ttf amiri/Amiri-Regular.ttf amiri/Amiri-Bold.ttf \
         cormorantsc/CormorantSC-SemiBold.ttf cormorantsc/CormorantSC-Bold.ttf cormorantsc/CormorantSC-Medium.ttf \
         "sourceserif4/SourceSerif4%5Bopsz,wght%5D.ttf" "sourceserif4/SourceSerif4-Italic%5Bopsz,wght%5D.ttf"; do
  f=$(basename "$p" | sed 's/%5B/[/;s/%5D/]/')
  curl -sSf -o "cache/fonts/$f" "$B/$p"
done
echo "données prêtes dans cache/"

#!/bin/bash
# download_ocr.sh - Download an image URL and run OCR
# Usage: download_ocr.sh <image_url>
# Returns: extracted text to stdout

URL="$1"
TMPFILE="/tmp/ocr_$(date +%s)_$$.jpg"

curl -sL -o "$TMPFILE" "$URL" 2>/dev/null
if [ ! -f "$TMPFILE" ] || [ $(stat -f%z "$TMPFILE") -lt 100 ]; then
    echo "ERROR: No se pudo descargar la imagen"
    rm -f "$TMPFILE"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
swift "$SCRIPT_DIR/ocr_swift.swift" "$TMPFILE" 2>/dev/null
rm -f "$TMPFILE"
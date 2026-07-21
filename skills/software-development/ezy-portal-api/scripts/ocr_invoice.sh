#!/bin/bash
# OCR an invoice image using macOS Vision framework (Swift)
# Usage: ./ocr_invoice.sh <image_path>
# Requires: Swift compiler (macOS built-in)
# Fallback when vision_analyze or tesseract aren't available

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SWIFT="$SCRIPT_DIR/ocr_invoice.swift"
IMG="$1"

if [ -z "$IMG" ]; then
    echo "Usage: $0 <image_path>"
    exit 1
fi

if [ ! -f "$IMG" ]; then
    echo "Error: File not found: $IMG"
    exit 1
fi

swift "$SWIFT" "$IMG" 2>&1
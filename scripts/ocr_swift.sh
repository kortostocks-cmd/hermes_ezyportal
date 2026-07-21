#!/bin/bash
# OCR wrapper - uses Swift + Apple Vision framework
# Usage: ocr_swift.sh <image_path>
# Returns: extracted text to stdout

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
swift "$SCRIPT_DIR/ocr_swift.swift" "$1" 2>/dev/null
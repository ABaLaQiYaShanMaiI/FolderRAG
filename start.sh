#!/usr/bin/env bash
# FolderKnowledgeSiteGeneratorForAI — Launch GUI
# Linux / macOS entry point

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================="
echo " FolderKnowledgeSiteGeneratorForAI"
echo " Document Knowledge Portal Generator"
echo " Loading..."
echo "============================================="
echo ""

python3 gui.py

if [ $? -ne 0 ]; then
    echo ""
    echo "[Error] Failed to start GUI."
    echo "Make sure Python 3 is installed."
    echo "Run: pip3 install -r requirements.txt"
    echo ""
    read -p "Press Enter to exit..."
fi
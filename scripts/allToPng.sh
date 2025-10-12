#!/bin/zsh

echo "Converting .jpg files to .png..."

# Check if magick command is available
if ! command -v magick &> /dev/null; then
    echo "magick command not found. Please install ImageMagick first."
    exit 1
fi

# Convert all .jpg files to .png and delete the original .jpg files
for jpg_file in **/*.jpg; do
    if [ -f "$jpg_file" ]; then
        png_file="${jpg_file%.jpg}.png"
        echo "Converting $jpg_file to $png_file"
        magick "$jpg_file" -quality 100 "$png_file"
        rm "$jpg_file"
    fi
done

echo "Conversion complete."

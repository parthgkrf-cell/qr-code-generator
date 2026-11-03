# High-Quality QR Code Generator

A modern, fast, and feature-rich QR Code Generator that produces ultra high-resolution raster images (PNG, JPEG up to 4096px, 300 DPI) and infinite-resolution lossless vector SVG files with custom logos, patterns, and colors.

Available as both a **Web App** (hosted on GitHub Pages) and a standalone **Python CLI script**.

---

## ✨ Features

- **Infinite Scalability (Vector SVG)**: Perfect for billboards, packaging, flyers, and large format printing.
- **Ultra High-Resolution PNG**: Export up to 4096×4096 px with 300 DPI print metadata.
- **Highest Error Correction (Level H)**: Recovers up to ~30% damage/redundancy, ensuring guaranteed scannability even on low-light cameras or textured print surfaces.
- **Center Logo Integration**: Upload your logo or icon with automatic safe scaling, padding, and high contrast masking.
- **Custom Pattern & Eye Styles**: Square (Classic), Dots, Rounded, Smooth Curved, Classy, and custom corner eyes.
- **Custom Colors**: Full HEX and RGB color pickers for foreground pattern and background.
- **100% Client-Side**: No data leaves your browser — fast, secure, and private.

---

## 🚀 Live Demo

Check out the live web app on GitHub Pages:
**[Launch QR Code Generator](https://parthgkrf-cell.github.io/qr-code-generator/)**

---

## 🐍 Python CLI Usage

If you prefer using Python in your terminal:

```bash
# Install dependencies
pip install "qrcode[pil]"

# Generate high-res QR code
python generate_qr.py "https://yourwebsite.com" -o my_qr.png --size 2048

# Generate vector SVG
python generate_qr.py "https://yourwebsite.com" -o my_qr.svg

# Embed a center logo
python generate_qr.py "https://yourwebsite.com" --logo "logo.png" -o qr_branded.png
```

---

## 📄 License
MIT License. Free to use for personal and commercial projects.

#!/usr/bin/env python3
"""
High-Quality QR Code Generator
==============================
Generates ultra-high resolution (PNG/JPEG) and lossless vector (SVG) QR codes from URLs/text.
Features:
- Highest error correction (Level H: ~30% redundancy recovery).
- Customizable output size / DPI (e.g., 2000x2000+ px for crisp print & digital use).
- Vector SVG export for infinite scalability.
- Optional center logo / branding icon with automatic safe sizing and padded border.
- Custom foreground and background colors (Hex, RGB, or named colors).
- Robust path handling (handles directories, missing extensions, quotes).
- Both CLI and importable Python API, plus an interactive prompt mode.

Requirements:
    pip install "qrcode[pil]"
"""

import sys
import os
import argparse
from typing import Optional

try:
    import qrcode
    from qrcode.constants import ERROR_CORRECT_H, ERROR_CORRECT_Q, ERROR_CORRECT_M, ERROR_CORRECT_L
    from qrcode.image.svg import SvgPathImage
    from PIL import Image
except ImportError:
    qrcode = None
    Image = None


ERROR_CORRECTION_MAP = {
    "L": 1,  # ~7% recovery
    "M": 0,  # ~15% recovery
    "Q": 3,  # ~25% recovery
    "H": 2,  # ~30% recovery (Recommended for high quality & logos)
}

VALID_IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".svg", ".webp", ".bmp"}


def _check_dependencies():
    """Ensure required packages are installed."""
    if qrcode is None or Image is None:
        print("\n[!] Missing required dependencies.", file=sys.stderr)
        print("Please install them by running:\n", file=sys.stderr)
        print("    pip install \"qrcode[pil]\"\n", file=sys.stderr)
        sys.exit(1)


def _clean_path(path: Optional[str]) -> Optional[str]:
    """Clean quotes and whitespace from path strings."""
    if not path:
        return None
    cleaned = path.strip().strip("'\"")
    return cleaned if cleaned else None


def _normalize_output_path(output_path: str) -> str:
    """Ensure output path has a valid extension and handles directory targets."""
    cleaned = _clean_path(output_path) or "qrcode_high_quality.png"

    # If the user passed an existing directory, save as qrcode_high_quality.png inside it
    if os.path.isdir(cleaned):
        return os.path.join(cleaned, "qrcode_high_quality.png")

    # If no extension or unknown extension, default to .png
    _, ext = os.path.splitext(cleaned)
    if not ext or ext.lower() not in VALID_IMAGE_EXTENSIONS:
        cleaned += ".png"

    return cleaned


def generate_qr(
    data: str,
    output_path: str = "qrcode.png",
    box_size: int = 20,
    border: int = 4,
    fill_color: str = "black",
    back_color: str = "white",
    error_correction: str = "H",
    logo_path: Optional[str] = None,
    logo_ratio: float = 0.22,
    target_size_px: Optional[int] = None,
    dpi: int = 300,
) -> str:
    """
    Generate a high-quality QR code.

    :param data: The link (URL) or text to encode.
    :param output_path: Destination file path (.png, .jpg, .svg).
    :param box_size: Number of pixels per QR module (default 20 for crisp high-res).
    :param border: Thickness of border in boxes (minimum 4 recommended by spec).
    :param fill_color: Color of the QR modules (e.g., 'black', '#1A56DB').
    :param back_color: Background color (e.g., 'white', '#FFFFFF').
    :param error_correction: 'L', 'M', 'Q', or 'H' (Default 'H' - highest resilience).
    :param logo_path: Optional path to an image file to embed in the center.
    :param logo_ratio: Max fraction of the QR code width that the logo will occupy (default 0.22).
    :param target_size_px: Optional exact output image size in pixels (e.g., 2048).
    :param dpi: Image DPI metadata for print quality (default 300).
    :return: Absolute path to the saved QR code.
    """
    _check_dependencies()

    if not data or not data.strip():
        raise ValueError("Data / URL cannot be empty.")

    output_path = _normalize_output_path(output_path)
    ec_level = ERROR_CORRECTION_MAP.get(error_correction.upper(), ERROR_CORRECT_H)
    is_svg = output_path.lower().endswith(".svg")

    # If SVG export requested
    if is_svg:
        qr = qrcode.QRCode(
            version=None,
            error_correction=ec_level,
            box_size=box_size,
            border=border,
            image_factory=SvgPathImage,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color=fill_color, back_color=back_color)

        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)
        img.save(output_path)
        print(f"[+] Scalable Vector QR Code (SVG) saved: {os.path.abspath(output_path)}")
        return os.path.abspath(output_path)

    # Standard Raster Image (PNG / JPG / etc.)
    qr = qrcode.QRCode(
        version=None,
        error_correction=ec_level,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    # Create base QR image
    qr_img = qr.make_image(fill_color=fill_color, back_color=back_color).convert("RGBA")

    # Optional: Center Logo Embedding
    cleaned_logo = _clean_path(logo_path)
    if cleaned_logo:
        if os.path.isdir(cleaned_logo):
            print(f"[!] Warning: '{cleaned_logo}' is a folder, not an image file. Skipping center logo.")
        elif not os.path.isfile(cleaned_logo):
            print(f"[!] Warning: Logo image '{cleaned_logo}' not found. Skipping center logo.")
        else:
            try:
                logo = Image.open(cleaned_logo).convert("RGBA")
                qr_width, qr_height = qr_img.size

                # Determine target logo size (safe limit <= 25% of QR width to guarantee scannability)
                max_logo_size = int(qr_width * min(logo_ratio, 0.25))
                logo.thumbnail((max_logo_size, max_logo_size), Image.Resampling.LANCZOS)

                # Create padded white container for high contrast
                pad = max(4, int(max_logo_size * 0.12))
                bg_size = (logo.size[0] + pad * 2, logo.size[1] + pad * 2)

                logo_background = Image.new("RGBA", bg_size, (255, 255, 255, 255))
                bg_pos = (
                    (qr_width - bg_size[0]) // 2,
                    (qr_height - bg_size[1]) // 2,
                )

                logo_pos = (
                    bg_pos[0] + pad,
                    bg_pos[1] + pad,
                )

                # Paste background patch then logo
                qr_img.paste(logo_background, bg_pos)
                qr_img.paste(logo, logo_pos, mask=logo)
                print(f"[+] Embedded center logo: {cleaned_logo}")
            except Exception as e:
                print(f"[!] Warning: Failed to load logo ({e}). Generating QR without logo.")

    # Optional resize to exact requested square resolution
    if target_size_px and target_size_px > 0:
        qr_img = qr_img.resize((target_size_px, target_size_px), Image.Resampling.LANCZOS)

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Save format handling
    ext = os.path.splitext(output_path)[1].lower()
    if ext in [".jpg", ".jpeg"]:
        rgb_img = Image.new("RGB", qr_img.size, (255, 255, 255))
        rgb_img.paste(qr_img, mask=qr_img.split()[3])
        rgb_img.save(output_path, "JPEG", quality=95, dpi=(dpi, dpi))
    else:
        qr_img.save(output_path, "PNG", dpi=(dpi, dpi))

    abs_path = os.path.abspath(output_path)
    print(f"\n[+] Success! High-Quality QR Code ({qr_img.width}x{qr_img.height} px, {dpi} DPI) saved to:")
    print(f"    {abs_path}")
    return abs_path


def interactive_mode():
    """Interactive prompt when run without command line arguments."""
    print("=" * 60)
    print("         HIGH QUALITY QR CODE GENERATOR")
    print("=" * 60)

    url = input("\nEnter Link / URL: ").strip().strip("'\"")
    while not url:
        print("Link cannot be empty.")
        url = input("Enter Link / URL: ").strip().strip("'\"")

    output = input("Output filename or folder [default: qrcode_high_quality.png]: ").strip().strip("'\"")
    if not output:
        output = "qrcode_high_quality.png"

    size_input = input("Exact pixel width/height (e.g. 1024, 2048) [press Enter for auto]: ").strip()
    target_size = int(size_input) if size_input.isdigit() else None

    fill_color = input("QR Code Color [default: black / hex e.g. #0D47A1]: ").strip() or "black"
    back_color = input("Background Color [default: white / hex e.g. #FFFFFF]: ").strip() or "white"

    logo_input = input("Path to center logo IMAGE file (e.g. logo.png, or press Enter to skip): ").strip().strip("'\"")
    logo_path = None
    if logo_input:
        if os.path.isdir(logo_input):
            print(f"Note: '{logo_input}' is a folder (not an image file). Skipping logo.")
        elif os.path.isfile(logo_input):
            logo_path = logo_input
        else:
            print(f"Note: File '{logo_input}' does not exist. Skipping logo.")

    print("\nGenerating...")
    generate_qr(
        data=url,
        output_path=output,
        fill_color=fill_color,
        back_color=back_color,
        logo_path=logo_path,
        target_size_px=target_size,
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate crystal-clear, high-quality QR codes for print and web."
    )
    parser.add_argument("url", nargs="?", help="Link or text to encode into the QR code")
    parser.add_argument(
        "-o", "--output",
        default="qrcode_high_res.png",
        help="Output image path (.png, .jpg, or .svg). Default: qrcode_high_res.png"
    )
    parser.add_argument(
        "-s", "--size",
        type=int,
        default=None,
        help="Target square dimension in pixels (e.g. 1024, 2048). Default: auto high-res"
    )
    parser.add_argument(
        "-b", "--box-size",
        type=int,
        default=20,
        help="Box size multiplier (default: 20 for ultra high-res)"
    )
    parser.add_argument(
        "--border",
        type=int,
        default=4,
        help="Border quiet zone width in blocks (default: 4)"
    )
    parser.add_argument(
        "--fill-color",
        default="black",
        help="Foreground / QR module color (e.g., 'black', '#0b57d0')"
    )
    parser.add_argument(
        "--back-color",
        default="white",
        help="Background color (e.g., 'white', '#f8f9fa')"
    )
    parser.add_argument(
        "--logo",
        default=None,
        help="Optional path to center logo / icon image"
    )
    parser.add_argument(
        "-ec", "--error-correction",
        choices=["L", "M", "Q", "H"],
        default="H",
        help="Error correction level (default: H - highest ~30%% recovery)"
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="DPI setting for print quality (default: 300)"
    )

    args = parser.parse_args()

    # If no URL provided via CLI arguments, launch friendly interactive mode
    if not args.url:
        interactive_mode()
        return

    generate_qr(
        data=args.url,
        output_path=args.output,
        box_size=args.box_size,
        border=args.border,
        fill_color=args.fill_color,
        back_color=args.back_color,
        error_correction=args.error_correction,
        logo_path=args.logo,
        target_size_px=args.size,
        dpi=args.dpi,
    )


if __name__ == "__main__":
    main()

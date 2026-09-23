from pathlib import Path
import re

from fpdf import FPDF
from PIL import Image


# ComicCraft project root:
# D:\code\ComicCraft
BASE_DIR = Path(__file__).resolve().parents[2]

STATIC_DIR = BASE_DIR / "static"
PANELS_DIR = STATIC_DIR / "panels"
EXPORTS_DIR = STATIC_DIR / "exports"


def _safe_text(value: str) -> str:
    """
    Convert generated text into something safely renderable
    by FPDF's built-in Helvetica font.
    """

    if not value:
        return ""

    text = str(value)

    replacements = {
        "\u2018": "'",
        "\u2019": "'",
        "\u201c": '"',
        "\u201d": '"',
        "\u2013": "-",
        "\u2014": "-",
        "\u2026": "...",
        "\u00a0": " ",
        "\u2022": "*",
        "\u2192": "->",
        "\u2190": "<-",
        "\u00a9": "(c)",
        "\u00ae": "(R)",
        "\u2122": "(TM)",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    # Remove problematic control characters.
    text = "".join(
        char
        for char in text
        if char in "\n\t" or ord(char) >= 32
    )

    # FPDF built-in Helvetica uses Latin-1.
    text = (
        text
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )

    # Break very long words so FPDF can wrap them.
    text = re.sub(
        r"(\S{40})",
        r"\1 ",
        text
    )

    return text.strip()


def _image_path_from_url(image_url: str) -> Path:
    """
    Convert a browser URL such as:

        /static/panels/panel_1.png

    into the actual local filesystem path.
    """

    if not image_url:
        return Path()

    clean_url = image_url.lstrip("/")

    if clean_url.startswith("static/"):
        return BASE_DIR / clean_url

    return STATIC_DIR / clean_url


def _safe_filename(value: str) -> str:
    """
    Convert a title into a safe Windows filename.
    """

    value = _safe_text(value)

    value = re.sub(
        r"[^a-zA-Z0-9_-]+",
        "_",
        value
    )

    value = value.strip("_")

    return value or "comic"


def save_pdf(title: str, panels: list[dict]) -> str:
    """
    Generate an A4 PDF containing the comic.

    Each panel is placed on its own page.
    """

    EXPORTS_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    pdf_filename = (
        f"{_safe_filename(title)}.pdf"
    )

    pdf_path = EXPORTS_DIR / pdf_filename

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    # A4 dimensions in mm.
    page_width = 210
    page_height = 297

    margin = 15
    content_width = page_width - (margin * 2)

    for index, panel in enumerate(
        panels,
        start=1
    ):

        pdf.add_page()

        # =================================================
        # PANEL TITLE
        # =================================================

        pdf.set_xy(
            margin,
            margin
        )

        pdf.set_font(
            "Helvetica",
            "B",
            16
        )

        pdf.cell(
            content_width,
            10,
            _safe_text(
                f"Panel {index}"
            ),
            align="C"
        )

        # =================================================
        # PANEL IMAGE
        # =================================================

        image_url = panel.get(
            "image_url",
            ""
        )

        image_path = _image_path_from_url(
            image_url
        )

        if image_path.exists():

            try:

                with Image.open(image_path) as image:

                    image_width, image_height = (
                        image.size
                    )

                    if (
                        image_width > 0
                        and image_height > 0
                    ):

                        max_width = content_width
                        max_height = 130

                        scale = min(
                            max_width / image_width,
                            max_height / image_height
                        )

                        rendered_width = (
                            image_width * scale
                        )

                        rendered_height = (
                            image_height * scale
                        )

                        image_x = (
                            page_width
                            - rendered_width
                        ) / 2

                        image_y = 30

                        pdf.image(
                            str(image_path),
                            x=image_x,
                            y=image_y,
                            w=rendered_width,
                            h=rendered_height
                        )

            except Exception as exc:

                # Keep PDF generation alive even if
                # one image cannot be opened.
                print(
                    f"Warning: could not add "
                    f"panel image {image_path}: {exc}"
                )

        else:

            print(
                f"Warning: panel image not found: "
                f"{image_path}"
            )

        # =================================================
        # TEXT AREA
        # =================================================

        pdf.set_xy(
            margin,
            168
        )

        # =================================================
        # CAPTION
        # =================================================

        caption = _safe_text(
            panel.get(
                "caption",
                ""
            )
        )

        if caption:

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                content_width,
                7,
                caption
            )

            pdf.ln(2)

        # =================================================
        # NARRATION
        # =================================================

        narration = _safe_text(
            panel.get(
                "narration",
                ""
            )
        )

        if narration:

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            narration_text = (
                f"Narration: {narration}"
            )

            pdf.multi_cell(
                content_width,
                6,
                narration_text
            )

            pdf.ln(2)

        # =================================================
        # DIALOGUE
        # =================================================

        dialogue = _safe_text(
            panel.get(
                "dialogue",
                ""
            )
        )

        if dialogue:

            pdf.set_font(
                "Helvetica",
                "",
                10
            )

            dialogue_text = (
                f"Dialogue: {dialogue}"
            )

            pdf.multi_cell(
                content_width,
                6,
                dialogue_text
            )

        # =================================================
        # FOOTER
        # =================================================

        pdf.set_y(
            page_height - 12
        )

        pdf.set_font(
            "Helvetica",
            "",
            8
        )

        pdf.cell(
            content_width,
            5,
            _safe_text(
                f"{title} - Panel {index}"
            ),
            align="C"
        )

    pdf.output(
        str(pdf_path)
    )

    print(
        f"PDF created: {pdf_path}"
    )

    return (
        f"/static/exports/{pdf_filename}"
    )
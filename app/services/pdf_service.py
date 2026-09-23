from datetime import datetime

from fpdf import FPDF
from PIL import Image

from app.config import get_settings


def _safe_text(value: str) -> str:
    """
    FPDF's default Helvetica font does not support
    every Unicode character. Replace unsupported
    characters instead of crashing PDF generation.
    """

    return (
        value
        .encode("latin-1", "replace")
        .decode("latin-1")
    )


def save_pdf(
    title: str,
    panels: list[dict]
) -> str:

    settings = get_settings()

    pdf = FPDF(
        orientation="P",
        unit="mm",
        format="A4"
    )

    pdf.set_auto_page_break(
        auto=True,
        margin=15
    )

    for panel in panels:

        pdf.add_page()

        pdf.set_font(
            "Helvetica",
            "B",
            18
        )

        pdf.multi_cell(
            0,
            10,
            _safe_text(
                f"Panel {panel['panel_number']}: "
                f"{panel['title']}"
            )
        )

        pdf.ln(3)

        image_path = (
            settings.output_dir.parent
            / panel["image_url"].lstrip("/")
        )

        if image_path.exists():

            with Image.open(image_path) as image:
                width, height = image.size

            max_width = 180
            max_height = 105

            ratio = min(
                max_width / width,
                max_height / height
            )

            new_width = width * ratio
            new_height = height * ratio

            pdf.image(
                str(image_path),
                x=15,
                y=35,
                w=new_width,
                h=new_height
            )

            pdf.set_y(
                35 + new_height + 7
            )

        pdf.set_font(
            "Helvetica",
            "I",
            10
        )

        pdf.multi_cell(
            0,
            6,
            _safe_text(
                panel["scene_description"]
            )
        )

        pdf.ln(2)

        if panel.get("caption"):

            pdf.set_font(
                "Helvetica",
                "B",
                11
            )

            pdf.multi_cell(
                0,
                6,
                _safe_text(
                    "CAPTION: "
                    + panel["caption"]
                )
            )

        if panel.get("narration"):

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                0,
                6,
                _safe_text(
                    "NARRATION: "
                    + panel["narration"]
                )
            )

        if panel.get("dialogue"):

            pdf.set_font(
                "Helvetica",
                "",
                11
            )

            pdf.multi_cell(
                0,
                6,
                _safe_text(
                    "DIALOGUE: "
                    + panel["dialogue"]
                )
            )

    filename = (
        f"comic_"
        f"{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        f".pdf"
    )

    path = settings.exports_dir / filename

    pdf.output(str(path))

    return f"/static/exports/{filename}"
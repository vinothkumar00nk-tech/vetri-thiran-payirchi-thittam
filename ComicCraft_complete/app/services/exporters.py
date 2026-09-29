from pathlib import Path

from fpdf import FPDF

from app.config import get_settings


def _safe_text(value: str) -> str:
    # Helvetica in fpdf2 is a Latin-1 font. Replace unsupported Unicode
    # characters so PDF export never crashes on smart punctuation/emojis.
    return (
        value.replace("—", "-")
        .replace("–", "-")
        .replace("“", '"')
        .replace("”", '"')
        .replace("’", "'")
        .replace("•", "-")
        .encode("latin-1", errors="replace")
        .decode("latin-1")
    )


class ComicPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", size=8)
        self.cell(
            0,
            10,
            f"ComicCraft - Page {self.page_no()}",
            align="C",
        )


def save_pdf(panels, comic_id: str) -> Path:
    settings = get_settings()
    pdf = ComicPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in panels:
        pdf.add_page()

        pdf.set_font("Helvetica", "B", 18)
        pdf.cell(
            0,
            12,
            _safe_text(f"Panel {panel.panel_number}: {panel.title}"),
            ln=True,
        )

        image_path = (
            settings.static_dir
            / panel.image_url.replace("/static/", "", 1)
        )

        if image_path.exists():
            pdf.image(str(image_path), x=15, y=35, w=180)
            pdf.set_y(145)
        else:
            pdf.set_y(40)
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 7, "Panel image is unavailable.")

        sections = [
            ("Scene", panel.scene_description),
            ("Caption", panel.caption),
            ("Narration", panel.narration),
        ]

        for heading, body in sections:
            pdf.set_font("Helvetica", "B", 11)
            pdf.multi_cell(0, 7, _safe_text(heading))
            pdf.set_font("Helvetica", size=10)
            pdf.multi_cell(0, 6, _safe_text(body))
            pdf.ln(2)

    output = settings.exports_dir / f"{comic_id}.pdf"
    pdf.output(str(output))
    return output

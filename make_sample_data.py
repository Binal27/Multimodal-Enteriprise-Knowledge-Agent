"""
make_sample_data.py — Generates two small SAMPLE documents (a PDF and a
PPTX) with a deliberately realistic conflict: the PDF quarterly report
states GAAP revenue, the slide deck states a non-GAAP adjusted figure for
the SAME quarter — mirroring how real companies often report two
different numbers for the same period.

These are placeholders so you have something to demo immediately. For
your final version, swap these out for real public filings — see
README.md for exactly how (SEC EDGAR 10-Q + a real investor deck).

Run:  python make_sample_data.py
"""
import os
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from pptx import Presentation
from pptx.util import Inches, Pt

OUT_DIR = "data"
os.makedirs(OUT_DIR, exist_ok=True)


def make_pdf():
    path = os.path.join(OUT_DIR, "quarterly_report.pdf")
    doc = SimpleDocTemplate(path, pagesize=letter)
    styles = getSampleStyleSheet()
    story = [
        Paragraph("Acme Corp — Q3 FY2026 Quarterly Report (Form 10-Q excerpt)", styles["Title"]),
        Spacer(1, 12),
        Paragraph(
            "The following unaudited financial results are presented in accordance "
            "with U.S. GAAP for the quarter ended September 30, 2026.",
            styles["Normal"],
        ),
        Spacer(1, 12),
        Table(
            [
                ["Metric", "Q3 FY2026", "Q3 FY2025"],
                ["Total Revenue (GAAP)", "$4.20M", "$3.65M"],
                ["Net Income (GAAP)", "$0.82M", "$0.60M"],
                ["Operating Margin", "18.1%", "15.4%"],
            ],
            style=TableStyle([
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ]),
        ),
        Spacer(1, 12),
        Paragraph(
            "Revenue reflects total consolidated revenue recognized under "
            "ASC 606, before adjustments for one-time items.",
            styles["Normal"],
        ),
    ]
    doc.build(story)
    print(f"Created {path}")


def make_pptx():
    path = os.path.join(OUT_DIR, "earnings_deck.pptx")
    prs = Presentation()

    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Acme Corp — Q3 FY2026 Investor Highlights"

    body = slide.shapes.add_textbox(Inches(0.5), Inches(1.5), Inches(9), Inches(3))
    tf = body.text_frame
    tf.text = "Q3 FY2026 Adjusted Revenue: $4.60M (non-GAAP, up 26% YoY)"
    p = tf.add_paragraph()
    p.text = "Adjusted revenue excludes deferred contract revenue and one-time refunds."
    p.font.size = Pt(14)
    p2 = tf.add_paragraph()
    p2.text = "See appendix for full GAAP reconciliation."
    p2.font.size = Pt(12)

    prs.save(path)
    print(f"Created {path}")


if __name__ == "__main__":
    make_pdf()
    make_pptx()

from io import BytesIO
from typing import Any, Dict, List

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas


def generate_bank_income_pdf(client_user_id: str, streams: List[Dict[str, Any]], totals: Dict[str, Any]) -> bytes:
    """
    Create a tiny PDF containing a title, the user id, and some derived totals.
    Returns raw PDF bytes suitable for application/pdf responses.
    """
    buffer = BytesIO()
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter

    y = height - 72
    c.setFont("Helvetica-Bold", 16)
    c.drawString(72, y, "Mock Plaid Bank Income Report")
    y -= 28

    c.setFont("Helvetica", 12)
    c.drawString(72, y, f"Client User ID: {client_user_id}")
    y -= 20

    c.drawString(72, y, f"Streams: {len(streams)}")
    y -= 18
    c.drawString(72, y, f"Average Net (sum of streams): {totals.get('sum_average_net', 0.0):.2f}")
    y -= 18
    c.drawString(72, y, f"Coverage Months: {totals.get('coverage_months', 12)}")
    y -= 18
    c.drawString(72, y, f"Coverage Type: {totals.get('coverage', 'FULL')}")
    y -= 28

    c.setFont("Helvetica-Bold", 12)
    c.drawString(72, y, "Streams")
    y -= 18
    c.setFont("Helvetica", 11)
    for idx, s in enumerate(streams[:10], start=1):  # avoid overflowing page
        line = f"{idx}. source={s.get('source')} cadence={s.get('cadence')} avg_net={s.get('average_net'):.2f} conf={s.get('confidence')}"
        c.drawString(72, y, line)
        y -= 16
        if y < 72:
            c.showPage()
            y = height - 72
            c.setFont("Helvetica", 11)

    c.showPage()
    c.save()
    return buffer.getvalue()

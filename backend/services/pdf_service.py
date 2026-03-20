from jinja2 import Environment, FileSystemLoader
import base64
from pathlib import Path
from ..config import settings

try:
    from weasyprint import HTML
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False


def generate_timetable_pdf(timetable_data: dict) -> bytes:
    env = Environment(loader=FileSystemLoader("backend/templates"))
    template = env.get_template("timetable_pdf.html")

    logo_path = Path(settings.college_logo_path)
    logo_b64 = ""
    if logo_path.exists():
        logo_b64 = base64.b64encode(logo_path.read_bytes()).decode()

    html_content = template.render(
        timetable=timetable_data,
        college_name=settings.college_name,
        logo_b64=logo_b64,
    )

    if WEASYPRINT_AVAILABLE:
        return HTML(string=html_content).write_pdf()
    else:
        # Return HTML as bytes if WeasyPrint not available
        return html_content.encode("utf-8")

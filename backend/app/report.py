"""Local, single-page repair verification reports."""
from pathlib import Path
from urllib.parse import unquote, urlsplit
from xml.sax.saxutils import escape

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import (Image, KeepInFrame, Paragraph, SimpleDocTemplate,
                               Spacer, Table, TableStyle)


_ROOT = Path(__file__).resolve().parents[2]


def _image_path(value: str | None) -> Path | None:
    """Resolve API image URLs locally without fetching remote resources."""
    if not value:
        return None
    url = urlsplit(str(value))
    path = unquote(url.path)
    for prefix, folder in (('/files/', 'runs'), ('/demo-files/', 'demo')):
        if path.startswith(prefix):
            base = (_ROOT / 'data' / folder).resolve()
            target = (base / path[len(prefix):]).resolve()
            return target if target.is_relative_to(base) and target.is_file() else None
    if url.scheme or url.netloc:
        return None
    target = Path(path)
    if not target.is_absolute():
        target = _ROOT / target
    return target if target.is_file() else None


def build_report(result: dict, out_pdf: str):
    """Write one A4 page of verification evidence using local images."""
    styles = getSampleStyleSheet()
    styles['BodyText'].fontSize = 9
    styles['BodyText'].leading = 12
    width = A4[0] - 72

    def paragraph(text, style: str = 'BodyText') -> Paragraph:
        return Paragraph(escape(str(text)).replace('\n', '<br/>'), styles[style])

    pct = result.get('percent_resolved')
    percent = f'{pct:g}% repaired' if pct is not None else 'Repair percentage unavailable'
    story = [paragraph('Sabooth — Repair verification report', 'Title'),
             paragraph(f"Complaint: {result.get('complaint_id', 'Unavailable')}"),
             paragraph(f"Result: {result.get('id', 'Unavailable')} | Created: {result.get('created_at', 'Unavailable')}"),
             Spacer(1, 10),
             paragraph(str(result.get('verdict', 'NEEDS_REVIEW')).replace('_', ' '), 'Heading1'),
             paragraph(percent, 'Heading2')]
    if result.get('simulated'):
        story.append(paragraph('Simulated repair (demo)'))
    story.append(paragraph('Reasons', 'Heading2'))
    for reason in result.get('reasons') or ['No reasons supplied.']:
        story.append(paragraph(f'• {reason}'))
    story.append(paragraph('Checks', 'Heading2'))
    rows = [[paragraph('Check'), paragraph('Status'), paragraph('Finding')]]
    for name, check in (result.get('checks') or {}).items():
        rows.append([paragraph(str(name).capitalize()), paragraph(check.get('status', 'skipped')),
                     paragraph(check.get('detail') or 'No detail supplied')])
    table = Table(rows, colWidths=[width * 0.18, width * 0.14, width * 0.68])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#E6ECF7')),
        ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#CBD5E1')),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 7),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
    ]))
    story.extend([table, Spacer(1, 12)])
    cells = []
    for key, label in (('before', 'Before'), ('heatmap', 'Repair heatmap')):
        cell = [paragraph(label, 'Heading3')]
        path = _image_path((result.get('images') or {}).get(key))
        if path is None:
            cell.append(paragraph('Image unavailable'))
        else:
            image = Image(str(path))
            scale = min((width / 2 - 16) / image.imageWidth, 175 / image.imageHeight)
            image.drawWidth = image.imageWidth * scale
            image.drawHeight = image.imageHeight * scale
            cell.append(image)
        cells.append(cell)
    images = Table([cells], colWidths=[width / 2, width / 2])
    images.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP')]))
    story.extend([images, paragraph('Explanation', 'Heading2'),
                  paragraph((result.get('explanation') or {}).get('en') or 'No explanation supplied.')])
    if (result.get('explanation') or {}).get('kn'):
        # Built-in PDF fonts cannot render Kannada reliably, including conjuncts.
        story.append(paragraph('Kannada omitted: a compatible font and shaping support are unavailable.'))
    output = Path(out_pdf)
    output.parent.mkdir(parents=True, exist_ok=True)
    document = SimpleDocTemplate(str(output), pagesize=A4, leftMargin=36, rightMargin=36,
                                 topMargin=32, bottomMargin=32,
                                 title='Sabooth repair verification report')
    def page_background(canvas, doc) -> None:
        """Give raster previews and printouts an opaque white page."""
        canvas.saveState()
        canvas.setFillColor(colors.white)
        canvas.rect(0, 0, *A4, fill=1, stroke=0)
        canvas.restoreState()

    document.build([KeepInFrame(width, A4[1] - 68, story, mode='shrink')],
                   onFirstPage=page_background)

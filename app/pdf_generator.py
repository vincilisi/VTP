import base64
import io

from reportlab.lib.pagesizes import A4
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


def genera_pdf(output_path, data):
    pdf = canvas.Canvas(output_path, pagesize=A4)
    width, height = A4

    pdf.setTitle("Riepilogo Servizi VTP")
    pdf.setFont("Helvetica-Bold", 20)
    pdf.drawString(40, height - 50, "Riepilogo Servizi VTP")

    pdf.setFont("Helvetica", 11)
    pdf.drawString(40, height - 90, f"Nome: {data.get('nome', '')}")
    pdf.drawString(260, height - 90, f"Cognome: {data.get('cognome', '')}")
    pdf.drawString(40, height - 110, f"Targa: {data.get('targa', '')}")
    pdf.drawString(260, height - 110, f"Modello: {data.get('modello', '')}")

    y = height - 170
    pdf.setFont("Helvetica-Bold", 10)
    pdf.drawString(40, y, "Giorno")
    pdf.drawString(90, y, "Servizio")
    pdf.drawString(420, y, "Aviaria")
    pdf.drawString(500, y, "Radiogeno")
    y -= 20

    pdf.setFont("Helvetica", 9)
    for riga in data.get("righe", []):
        if y < 170:
            pdf.showPage()
            y = height - 50
            pdf.setFont("Helvetica", 9)

        pdf.drawString(40, y, str(riga.get("giorno", "")))
        pdf.drawString(90, y, str(riga.get("servizio", ""))[:60])
        pdf.drawString(420, y, str(riga.get("aviaria", 0)))
        pdf.drawString(500, y, str(riga.get("radiogeno", 0)))
        y -= 18

    totale_aviaria = data.get("totale_aviaria", 0)
    totale_radiogeno = data.get("totale_radiogeno", 0)
    totale_complessivo = totale_aviaria + totale_radiogeno

    pdf.line(40, 120, width - 40, 120)
    pdf.setFont("Helvetica-Bold", 12)
    pdf.drawString(40, 95, f"Totale Aviaria: {totale_aviaria} EUR")
    pdf.drawString(300, 95, f"Totale Radiogeno: {totale_radiogeno} EUR")
    pdf.drawString(40, 70, f"Totale complessivo: {totale_complessivo} EUR")

    pdf.drawString(350, 70, "Firma:")
    firma = data.get("firma", "")
    if firma.startswith("data:image/"):
        encoded_image = firma.split(",", 1)[1]
        image = ImageReader(io.BytesIO(base64.b64decode(encoded_image)))
        pdf.drawImage(image, 400, 25, width=140, height=40, preserveAspectRatio=True, mask="auto")
    else:
        pdf.rect(400, 25, 140, 40)

    pdf.save()
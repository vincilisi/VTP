from pathlib import Path
import io
import re

import pdfplumber

from fastapi import (
    FastAPI,
    File,
    UploadFile,
    Body
)

from fastapi.responses import (
    HTMLResponse,
    FileResponse
)

from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from starlette.requests import Request

from app.pdf_generator import genera_pdf


BASE_DIR = Path(__file__).resolve().parent

app = FastAPI(title="VTP WebApp")


app.mount(
    "/static",
    StaticFiles(
        directory=BASE_DIR / "static"
    ),
    name="static"
)

templates = Jinja2Templates(
    directory=BASE_DIR / "templates"
)


@app.get("/", response_class=HTMLResponse)
def home(request: Request):

    return templates.TemplateResponse(
        request=request,
        name="index.html"
    )


@app.get("/service-worker.js", include_in_schema=False)
def service_worker():
    return FileResponse(
        BASE_DIR / "static" / "service-worker.js",
        media_type="application/javascript",
        headers={"Cache-Control": "no-cache"}
    )


def service_row(giorno: str, service: str):
    upper = service.upper()

    if "VENEZIA TERMINAL PASSEGGERI" not in upper:
        return None

    aviaria = 0
    radiogeno = 0

    if "SALONI" in upper:
        aviaria = 15

    if "USCITA SALONI" in upper:
        aviaria = 15

    if "RXM" in upper or "RXP" in upper:
        radiogeno = 2

    return {
        "giorno": giorno,
        "servizio": service,
        "aviaria": aviaria,
        "radiogeno": radiogeno
    }


def parse_table_services(table):
    rows = []

    for table_row in table:
        cells = [" ".join((cell or "").split()) for cell in table_row]
        service = " ".join(cells)

        if "VENEZIA TERMINAL PASSEGGERI" not in service.upper():
            continue

        day_match = re.search(r"\b(\d{1,2})\b", service)
        giorno = day_match.group(1) if day_match else ""
        row = service_row(giorno, service)

        if row:
            rows.append(row)

    return rows


def parse_services(text: str):
    rows = []
    day_pattern = re.compile(
        r"(?<!\d)(\d{1,2})\s+(?:LUN|MAR|MER|GIO|VEN|SAB|DOM)\b",
        flags=re.IGNORECASE
    )
    day_matches = list(day_pattern.finditer(text))

    for index, day_match in enumerate(day_matches):
        end = (
            day_matches[index + 1].start()
            if index + 1 < len(day_matches)
            else len(text)
        )
        giorno = day_match.group(1)
        service = " ".join(text[day_match.start():end].split())
        row = service_row(giorno, service)

        if row:
            rows.append(row)

    return rows


@app.post("/api/estrai")
async def estrai(
    file: UploadFile = File(...)
):

    content = await file.read()

    with pdfplumber.open(
        io.BytesIO(content)
    ) as pdf:

        rows = []

        for page in pdf.pages:
            tables = page.extract_tables()

            if tables:
                for table in tables:
                    rows.extend(parse_table_services(table))
            else:
                rows.extend(parse_services(page.extract_text() or ""))

    return {
        "ok": True,
        "righe": rows,
        "totale_aviaria": sum(
            r["aviaria"]
            for r in rows
        ),
        "totale_radiogeno": sum(
            r["radiogeno"]
            for r in rows
        )
    }


@app.post("/api/genera-pdf")
async def genera_pdf_endpoint(
    data: dict = Body(...)
):

    output_dir = (
        BASE_DIR.parent / "output"
    )

    output_dir.mkdir(
        exist_ok=True
    )

    pdf_path = (
        output_dir /
        "rimborso.pdf"
    )

    genera_pdf(
        str(pdf_path),
        data
    )

    return FileResponse(
        str(pdf_path),
        filename="rimborso.pdf",
        media_type="application/pdf"
    )
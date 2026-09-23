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


def parse_services(text: str):
    rows = []

    for line in text.splitlines():
        service = " ".join(line.split())
        upper = service.upper()

        if "VENEZIA TERMINAL PASSEGGERI" not in upper:
            continue

        day_match = re.match(
            r"(\d{1,2})\s+(?:LUN|MAR|MER|GIO|VEN|SAB|DOM)\b",
            upper
        )

        if not day_match:
            continue

        giorno = day_match.group(1)

        aviaria = 0
        radiogeno = 0

        if "SALONI" in upper:
            aviaria = 15

        if "USCITA SALONI" in upper:
            aviaria = 15

        if (
            "RXM" in upper or
            "RXP" in upper
        ):
            radiogeno = 2

        rows.append(
            {
                "giorno": giorno,
                "servizio": service,
                "aviaria": aviaria,
                "radiogeno": radiogeno
            }
        )

    return rows


@app.post("/api/estrai")
async def estrai(
    file: UploadFile = File(...)
):

    content = await file.read()

    with pdfplumber.open(
        io.BytesIO(content)
    ) as pdf:

        text = ""

        for page in pdf.pages:

            text += (
                page.extract_text(layout=True)
                or ""
            ) + "\n"

    rows = parse_services(text)

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
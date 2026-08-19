from __future__ import annotations

import io
import os
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse, HTMLResponse, Response
from openpyxl import Workbook
from openpyxl.styles import Font
from pydantic import BaseModel

from .caldav_client import CalDavError, CalDavClient, import_events
from .ics_builder import build_event_ics, build_ics
from .transformer import build_events
from .xlsx_parser import parse_workbook

app = FastAPI(title="CarboCal", version="0.3.0")

_TEMPLATES = Path(__file__).parent / "templates"
_STATIC = Path(__file__).parent / "static"

DEFAULT_SERVER = os.environ.get("CARBOCAL_SERVER_URL", "https://mail.smiden.fr")

_TEMPLATE_COLUMNS = ["Sujet", "Date", "Heure début", "Heure fin", "Lieu", "Invités"]


class Credentials(BaseModel):
    server: str
    login: str
    password: str


def _load_rows(content: bytes, filename: str) -> tuple[list, list[str]]:
    try:
        rows, errors = parse_workbook(io.BytesIO(content))
    except Exception as exc:  # openpyxl raises various exceptions
        raise HTTPException(status_code=400, detail=f"Lecture du fichier impossible : {exc}")
    if not rows:
        detail = "\n".join(errors) or "aucune ligne exploitable"
        raise HTTPException(status_code=400, detail=detail)
    return rows, errors


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    html = (_TEMPLATES / "index.html").read_text(encoding="utf-8")
    return html.replace("__CARBOCAL_SERVER__", DEFAULT_SERVER)


@app.get("/favicon.ico")
async def favicon_ico() -> FileResponse:
    return FileResponse(_STATIC / "favicon.ico", media_type="image/x-icon")


@app.get("/favicon.png")
async def favicon_png() -> FileResponse:
    return FileResponse(_STATIC / "favicon.png", media_type="image/png")


@app.get("/logo.png")
async def logo() -> FileResponse:
    return FileResponse(_STATIC / "logo.png", media_type="image/png")


@app.get("/template")
async def template() -> Response:
    wb = Workbook()
    ws = wb.active
    ws.title = "Import_Carbonio"
    ws.append(_TEMPLATE_COLUMNS)
    for cell in ws[1]:
        cell.font = Font(bold=True)
    ws.freeze_panes = "A2"
    ws.column_dimensions["A"].width = 40
    ws.column_dimensions["B"].width = 14
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 14
    ws.column_dimensions["E"].width = 26
    ws.column_dimensions["F"].width = 40
    buf = io.BytesIO()
    wb.save(buf)
    return Response(
        content=buf.getvalue(),
        media_type=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        headers={
            "Content-Disposition": 'attachment; filename="Modele_Import_Carbonio.xlsx"'
        },
    )


@app.post("/convert")
async def convert(
    file: UploadFile = File(...),
    organizer: str = Form(default=""),
    tzid: str = Form(default="Europe/Paris"),
) -> Response:
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Le fichier doit être au format .xlsx")

    content = await file.read()
    rows, parse_errors = _load_rows(content, file.filename)
    result = build_events(rows)
    ics = build_ics(
        result.single_events,
        result.recurring_events,
        organizer=organizer.strip() or None,
        tzid=tzid,
    )
    filename = Path(file.filename).stem + ".ics"
    headers = {
        "Content-Disposition": f'attachment; filename="{filename}"',
        "X-CarboCal-Recurring": str(len(result.recurring_events)),
        "X-CarboCal-Single": str(len(result.single_events)),
        "X-CarboCal-Skipped": str(result.rows_skipped),
        "X-CarboCal-Errors": str(len(parse_errors) + len(result.errors)),
    }
    return Response(
        content=ics,
        media_type="text/calendar; charset=utf-8",
        headers=headers,
    )


@app.post("/calendars")
async def calendars(credentials: Credentials) -> dict:
    if not credentials.server.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL du serveur invalide")
    try:
        client = CalDavClient(
            credentials.server, credentials.login, credentials.password
        )
        return {"calendars": client.list_calendars()}
    except CalDavError as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.post("/import")
async def import_caldav(
    file: UploadFile = File(...),
    server: str = Form(...),
    login: str = Form(...),
    password: str = Form(...),
    calendar: str = Form(...),
    organizer: str = Form(default=""),
    tzid: str = Form(default="Europe/Paris"),
    delay: float = Form(default=0.5),
) -> dict:
    if not file.filename or not file.filename.lower().endswith((".xlsx", ".xlsm")):
        raise HTTPException(status_code=400, detail="Le fichier doit être au format .xlsx")
    if not server.startswith(("http://", "https://")):
        raise HTTPException(status_code=400, detail="URL du serveur invalide")

    content = await file.read()
    rows, parse_errors = _load_rows(content, file.filename)
    result = build_events(rows)

    organizer = organizer.strip() or login
    payloads = [
        (ev.subject, build_event_ics(ev, organizer=organizer, tzid=tzid, method="REQUEST"))
        for ev in result.single_events + result.recurring_events
    ]

    try:
        report = import_events(
            server,
            login,
            password,
            calendar,
            payloads,
            delay=delay,
        )
    except CalDavError as exc:
        raise HTTPException(status_code=502, detail=str(exc))

    report["skipped"] = result.rows_skipped
    report["parse_errors"] = parse_errors + result.errors
    return report
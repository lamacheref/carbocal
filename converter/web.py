from __future__ import annotations

import io
import time
from pathlib import Path

from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import HTMLResponse, Response
from pydantic import BaseModel

from .caldav_client import CalDavError, CalDavClient, import_events
from .ics_builder import build_event_ics, build_ics
from .transformer import build_events
from .xlsx_parser import parse_workbook

app = FastAPI(title="SendRendezvous", version="0.3.0")

_TEMPLATES = Path(__file__).parent / "templates"


class Credentials(BaseModel):
    server: str
    login: str
    password: str


def _load_rows(content: bytes, filename: str) -> tuple[list, list[str]]:
    try:
        rows, errors = parse_workbook(io.BytesIO(content))
    except Exception as exc:  # openpyxl raises various exceptions
        raise HTTPException(status_code=400, detail=f"Lecture du XLSX impossible : {exc}")
    if not rows:
        detail = "\n".join(errors) or "aucune ligne exploitable"
        raise HTTPException(status_code=400, detail=detail)
    return rows, errors


@app.get("/", response_class=HTMLResponse)
async def index() -> str:
    return (_TEMPLATES / "index.html").read_text(encoding="utf-8")


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
        "X-SendRendezvous-Recurring": str(len(result.recurring_events)),
        "X-SendRendezvous-Single": str(len(result.single_events)),
        "X-SendRendezvous-Skipped": str(result.rows_skipped),
        "X-SendRendezvous-Errors": str(len(parse_errors) + len(result.errors)),
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
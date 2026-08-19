from __future__ import annotations

import logging
import time

import caldav

logger = logging.getLogger(__name__)


class CalDavError(Exception):
    pass


class CalDavClient:
    """Client CalDAV pour Carbonio/Zimbra (base : <serveur>/dav/)."""

    def __init__(self, server_url: str, username: str, password: str, timeout: int = 60):
        base = server_url.rstrip("/")
        self.dav_url = f"{base}/dav/"
        try:
            self.client = caldav.DAVClient(
                url=self.dav_url,
                username=username,
                password=password,
                timeout=timeout,
            )
        except Exception as exc:
            raise CalDavError(f"impossible d'initialiser le client CalDAV : {exc}") from exc

    def _calendar(self, href: str):
        return caldav.Calendar(client=self.client, url=href, parent=None)

    def list_calendars(self) -> list[dict]:
        try:
            principal = self.client.principal()
            calendars = principal.calendars()
        except Exception as exc:
            raise CalDavError(
                f"connexion ou énumération des calendriers impossible "
                f"({self.dav_url}) : {exc}"
            ) from exc

        result = []
        for cal in calendars:
            display = None
            try:
                display = cal.get_display_name()
            except Exception:
                pass
            name = display or cal.name or cal.canonical_url
            result.append(
                {
                    "name": name,
                    "href": cal.canonical_url,
                }
            )
        result.sort(key=lambda c: (c["name"].lower() != "calendar", c["name"].lower()))
        return result

    def find_calendar(self, target: str) -> str:
        target = target.strip()
        for cal in self.list_calendars():
            if cal["href"] == target or cal["href"].rstrip("/") == target.rstrip("/"):
                return cal["href"]
        for cal in self.list_calendars():
            if cal["name"].lower() == target.lower():
                return cal["href"]
        names = ", ".join(f"{c['name']} ({c['href']})" for c in self.list_calendars())
        raise CalDavError(
            f"calendrier « {target} » introuvable. Disponibles : {names or 'aucun'}"
        )

    def create_event(self, calendar_href: str, payload: bytes) -> str:
        try:
            cal = self._calendar(calendar_href)
            event = cal.save_event(payload)
            return event.canonical_url
        except Exception as exc:
            raise CalDavError(f"création du rendez-vous impossible : {exc}") from exc


def import_events(
    server_url: str,
    username: str,
    password: str,
    calendar_target: str,
    payloads: list[tuple[str, bytes]],
    organizer: str | None = None,
    delay: float = 0.0,
    dry_run: bool = False,
) -> dict:
    """Crée chaque événement (subject, payload ICS) dans le calendrier CalDAV choisi.

    Retourne un rapport : {created, errors: [{subject, error}]}.
    """
    client = CalDavClient(server_url, username, password)
    calendar_href = client.find_calendar(calendar_target)

    report = {"created": 0, "errors": []}
    for index, (subject, payload) in enumerate(payloads):
        if dry_run:
            report["created"] += 1
            continue
        try:
            client.create_event(calendar_href, payload)
            report["created"] += 1
        except CalDavError as exc:
            report["errors"].append({"subject": subject, "error": str(exc)})
        if delay and index < len(payloads) - 1:
            time.sleep(delay)
    return report
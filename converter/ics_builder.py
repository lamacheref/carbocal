from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from icalendar import (
    Calendar,
    Event,
    Timezone,
    TimezoneDaylight,
    TimezoneStandard,
    vCalAddress,
)

from .model import RecurringEvent, SingleEvent

WEEKDAY_NAMES = ["MO", "TU", "WE", "TH", "FR", "SA", "SU"]

CALENDAR_PRODID = "-//CarboCal//Convertisseur//FR"


def _vtimezone(tzid: str) -> Timezone:
    tz = Timezone()
    tz.add("tzid", tzid)

    standard = TimezoneStandard()
    standard.add("dtstart", datetime(1970, 10, 25, 3, 0))
    standard.add("tzoffsetto", timedelta(hours=1))
    standard.add("tzoffsetfrom", timedelta(hours=2))
    standard.add("rrule", "FREQ=YEARLY;BYMONTH=10;BYDAY=-1SU")
    standard.add("tzname", "CET")

    daylight = TimezoneDaylight()
    daylight.add("dtstart", datetime(1970, 3, 29, 2, 0))
    daylight.add("tzoffsetto", timedelta(hours=2))
    daylight.add("tzoffsetfrom", timedelta(hours=1))
    daylight.add("rrule", "FREQ=YEARLY;BYMONTH=3;BYDAY=-1SU")
    daylight.add("tzname", "CEST")

    tz.add_component(standard)
    tz.add_component(daylight)
    return tz


def _local(d: datetime, tz: ZoneInfo) -> datetime:
    if d.tzinfo is None:
        return d.replace(tzinfo=tz)
    return d


def _add_attendees(event: Event, attendees: list[str], organizer: str | None) -> None:
    if organizer:
        org = vCalAddress(f"mailto:{organizer}")
        org.params["CN"] = organizer
        event["organizer"] = org
    for email in attendees:
        attendee = vCalAddress(f"mailto:{email}")
        attendee.params["CN"] = email
        attendee.params["ROLE"] = "REQ-PARTICIPANT"
        attendee.params["PARTSTAT"] = "NEEDS-ACTION"
        attendee.params["RSVP"] = "TRUE"
        event.add("attendee", attendee)


def _single_event(
    ev: SingleEvent, tz: ZoneInfo, organizer: str | None
) -> Event:
    event = Event()
    event["uid"] = ev.uid
    event.add("summary", ev.subject)
    if ev.all_day:
        event.add("dtstart", ev.date)
        event.add("dtend", ev.date + timedelta(days=1))
    else:
        start = _local(datetime.combine(ev.date, ev.start), tz)
        end = _local(datetime.combine(ev.date, ev.end), tz)
        event.add("dtstart", start)
        event.add("dtend", end)
    if ev.location:
        event.add("location", ev.location)
    _add_attendees(event, ev.attendees, organizer)
    return event


def _recurring_event(
    ev: RecurringEvent, tz: ZoneInfo, organizer: str | None
) -> Event:
    event = Event()
    event["uid"] = ev.uid
    event.add("summary", ev.subject)
    if ev.all_day:
        event.add("dtstart", ev.first)
    else:
        start = _local(datetime.combine(ev.first, ev.start), tz)
        end = _local(datetime.combine(ev.first, ev.end), tz)
        event.add("dtstart", start)
        event.add("dtend", end)
    if ev.location:
        event.add("location", ev.location)

    byday = WEEKDAY_NAMES[ev.weekday]
    last_cadence = _cadence_last(ev.first, ev.until, ev.interval)
    if ev.all_day:
        until_fmt = f"{last_cadence:%Y%m%d}"
    else:
        until_fmt = (
            f"{datetime.combine(last_cadence, ev.end).replace(tzinfo=tz).astimezone(timezone.utc).replace(tzinfo=None):%Y%m%dT%H%M%SZ}"
        )
    rrule = f"FREQ=WEEKLY;INTERVAL={ev.interval};BYDAY={byday};UNTIL={until_fmt}"
    event.add("rrule", rrule)

    if ev.rdates:
        if ev.all_day:
            rdates = list(ev.rdates)
        else:
            rdates = [_local(datetime.combine(d, ev.start), tz) for d in ev.rdates]
        event.add("rdate", rdates)
    if ev.exdates:
        if ev.all_day:
            exdates = list(ev.exdates)
        else:
            exdates = [_local(datetime.combine(d, ev.start), tz) for d in ev.exdates]
        event.add("exdate", exdates)

    _add_attendees(event, ev.attendees, organizer)
    return event


def _cadence_last(first, until, interval) -> date:
    current = first
    last = first
    while current <= until:
        last = current
        current += timedelta(days=7 * interval)
    return last


def _event_for(
    event: SingleEvent | RecurringEvent, tz: ZoneInfo, organizer: str | None
) -> Event:
    if isinstance(event, SingleEvent):
        return _single_event(event, tz, organizer)
    return _recurring_event(event, tz, organizer)


def _new_calendar(method: str, tzid: str) -> Calendar:
    cal = Calendar()
    cal.add("prodid", CALENDAR_PRODID)
    cal.add("version", "2.0")
    cal.add("calscale", "GREGORIAN")
    cal.add("method", method)
    cal.add_component(_vtimezone(tzid))
    return cal


def build_ics(
    single_events: list[SingleEvent],
    recurring_events: list[RecurringEvent],
    organizer: str | None = None,
    tzid: str = "Europe/Paris",
    method: str = "PUBLISH",
) -> bytes:
    tz = ZoneInfo(tzid)
    cal = _new_calendar(method, tzid)

    for ev in single_events:
        cal.add_component(_single_event(ev, tz, organizer))
    for ev in recurring_events:
        cal.add_component(_recurring_event(ev, tz, organizer))

    return cal.to_ical()


def build_event_ics(
    event: SingleEvent | RecurringEvent,
    organizer: str | None = None,
    tzid: str = "Europe/Paris",
    method: str = "REQUEST",
) -> bytes:
    tz = ZoneInfo(tzid)
    cal = _new_calendar(method, tzid)
    cal.add_component(_event_for(event, tz, organizer))
    return cal.to_ical()
from __future__ import annotations

import uuid
from collections import Counter, defaultdict
from datetime import date, timedelta

from .model import ConversionResult, RawRow, RecurringEvent, SingleEvent

_NAMESPACE = uuid.NAMESPACE_URL


def make_uid(*parts) -> str:
    key = "|".join(str(p) for p in parts)
    return f"{uuid.uuid5(_NAMESPACE, key)}@sendrendezvous"


def _series_key(row: RawRow):
    return (
        row.subject,
        row.start,
        row.end,
        row.all_day,
        row.location,
        tuple(sorted(row.attendees)),
    )


def _cadence_dates(first: date, until: date, interval: int) -> list[date]:
    dates: list[date] = []
    current = first
    while current <= until:
        dates.append(current)
        current += timedelta(days=7 * interval)
    return dates


def build_events(rows: list[RawRow]) -> ConversionResult:
    result = ConversionResult(rows_total=len(rows))
    groups: dict[tuple, list[RawRow]] = defaultdict(list)
    for row in rows:
        groups[_series_key(row)].append(row)

    for members in groups.values():
        members.sort(key=lambda r: r.date)
        if len(members) == 1:
            m = members[0]
            result.single_events.append(
                SingleEvent(
                    uid=make_uid(
                        "single", m.subject, m.date, m.start, m.end, m.location, m.attendees
                    ),
                    subject=m.subject,
                    date=m.date,
                    start=m.start,
                    end=m.end,
                    location=m.location,
                    attendees=list(m.attendees),
                )
            )
            continue

        dates = [m.date for m in members]
        weekdays = {d.weekday() for d in dates}
        gaps = [(dates[i + 1] - dates[i]).days for i in range(len(dates) - 1)]
        periodic = len(weekdays) == 1 and all(gap % 7 == 0 for gap in gaps)

        if not periodic:
            for m in members:
                result.single_events.append(
                    SingleEvent(
                        uid=make_uid(
                            "single",
                            m.subject,
                            m.date,
                            m.start,
                            m.end,
                            m.location,
                            m.attendees,
                        ),
                        subject=m.subject,
                        date=m.date,
                        start=m.start,
                        end=m.end,
                        location=m.location,
                        attendees=list(m.attendees),
                    )
                )
            continue

        weekly_gaps = [gap // 7 for gap in gaps]
        interval = Counter(weekly_gaps).most_common(1)[0][0]
        first, until = dates[0], dates[-1]
        cadence = _cadence_dates(first, until, interval)
        source = set(dates)
        rdates = sorted(source - set(cadence))
        exdates = sorted(set(cadence) - source)

        result.recurring_events.append(
            RecurringEvent(
                uid=make_uid(
                    "recur",
                    members[0].subject,
                    members[0].start,
                    members[0].end,
                    members[0].location,
                    members[0].attendees,
                    interval,
                    first,
                ),
                subject=members[0].subject,
                start=members[0].start,
                end=members[0].end,
                location=members[0].location,
                attendees=list(members[0].attendees),
                weekday=first.weekday(),
                interval=interval,
                first=first,
                until=until,
                rdates=rdates,
                exdates=exdates,
            )
        )

    return result
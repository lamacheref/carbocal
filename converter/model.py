from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, time


@dataclass
class RawRow:
    line: int
    subject: str
    date: date
    start: time | None = None
    end: time | None = None
    location: str = ""
    attendees: list[str] = field(default_factory=list)

    @property
    def all_day(self) -> bool:
        return self.start is None and self.end is None


@dataclass
class SingleEvent:
    uid: str
    subject: str
    date: date
    start: time | None = None
    end: time | None = None
    location: str = ""
    attendees: list[str] = field(default_factory=list)

    @property
    def all_day(self) -> bool:
        return self.start is None and self.end is None


@dataclass
class RecurringEvent:
    uid: str
    subject: str
    start: time | None = None
    end: time | None = None
    location: str = ""
    attendees: list[str] = field(default_factory=list)
    weekday: int = 0
    interval: int = 1
    first: date = field(default_factory=date)
    until: date = field(default_factory=date)
    rdates: list[date] = field(default_factory=list)
    exdates: list[date] = field(default_factory=list)

    @property
    def all_day(self) -> bool:
        return self.start is None and self.end is None


@dataclass
class ConversionResult:
    rows_total: int = 0
    rows_skipped: int = 0
    single_events: list[SingleEvent] = field(default_factory=list)
    recurring_events: list[RecurringEvent] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
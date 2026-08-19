from __future__ import annotations

import argparse
import getpass
import sys

from . import __version__
from .caldav_client import CalDavError, import_events
from .ics_builder import build_event_ics, build_ics
from .transformer import build_events
from .xlsx_parser import parse_workbook


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="carbocal",
        description="Convertit un XLSX de rendez-vous en .ics ou l'importe dans Carbonio via CalDAV.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument("-i", "--input", required=True, help="fichier XLSX source")
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        help="fichier .ics de sortie (mode convert)",
    )
    parser.add_argument(
        "--sheet", default=None, help="nom de la feuille à lire (défaut : première feuille)"
    )
    parser.add_argument(
        "--organizer", default=None, help="email du compte organisateur"
    )
    parser.add_argument(
        "--tzid", default="Europe/Paris", help="fuseau horaire (défaut : Europe/Paris)"
    )

    sub = parser.add_subparsers(dest="cmd", metavar="COMMANDE")
    imp = sub.add_parser(
        "import", help="import automatique dans Carbonio via CalDAV"
    )
    imp.add_argument(
        "--server", required=True, help="URL du serveur, ex. https://mail.smiden.fr"
    )
    imp.add_argument("--login", required=True, help="compte CalDAV")
    imp.add_argument("--password", default=None, help="mot de passe (sinon saisi)")
    imp.add_argument(
        "--calendar", default="Calendar", help="calendrier cible (défaut : Calendar)"
    )
    imp.add_argument(
        "--delay", type=float, default=0.5, help="pause en secondes entre deux créations"
    )
    imp.add_argument(
        "--dry-run", action="store_true", help="vérifie sans créer de rendez-vous"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_arg_parser().parse_args(argv)

    rows, parse_errors = parse_workbook(args.input, args.sheet)
    if not rows:
        for err in parse_errors:
            print(f"ERREUR : {err}", file=sys.stderr)
        return 1
    result = build_events(rows)

    if args.cmd == "import":
        return _run_import(args, result, parse_errors)
    return _run_convert(args, result, parse_errors)


def _run_convert(args, result, parse_errors) -> int:
    if not args.output:
        print("L'option -o/--output est requise en mode convert", file=sys.stderr)
        return 2
    ics = build_ics(
        result.single_events,
        result.recurring_events,
        organizer=args.organizer,
        tzid=args.tzid,
    )
    with open(args.output, "wb") as fh:
        fh.write(ics)
    print(f"Lignes lues : {result.rows_total}")
    print(f"Séries récurrentes : {len(result.recurring_events)}")
    print(f"Événements unitaires : {len(result.single_events)}")
    for err in parse_errors + result.errors:
        print(f"Avertissement : {err}")
    print(f"Fichier écrit : {args.output}")
    return 0


def _run_import(args, result, parse_errors) -> int:
    password = args.password
    if not password:
        password = getpass.getpass(f"Mot de passe {args.login}@{args.server} : ")
    payloads = [
        (
            ev.subject,
            build_event_ics(
                ev, organizer=args.organizer or args.login, tzid=args.tzid, method="REQUEST"
            ),
        )
        for ev in result.single_events + result.recurring_events
    ]
    print(f"Rendez-vous à créer : {len(payloads)}")
    if args.dry_run:
        print("Mode dry-run : aucune création effectuée.")
    try:
        report = import_events(
            args.server,
            args.login,
            password,
            args.calendar,
            payloads,
            delay=args.delay,
            dry_run=args.dry_run,
        )
    except CalDavError as exc:
        print(f"ERREUR : {exc}", file=sys.stderr)
        return 1

    print(f"Créés : {report['created']}")
    for err in report["errors"]:
        print(f"Échec : {err['subject']} — {err['error']}")
    for err in parse_errors + result.errors:
        print(f"Avertissement : {err}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
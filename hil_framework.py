"""Stand-in for the real HIL framework so the test items run off-hardware."""

from __future__ import annotations

import sqlite3
from functools import wraps
from typing import Any


class Hdb:
    """HDB — the historical database (sqlite): stores what a run measured and
    checked, plus the equations — SQL conditions over that history — that
    decide when a display icon (OIL, ...) lights up."""

    def __init__(self, name: str) -> None:
        self.name = name
        self._conn = sqlite3.connect(":memory:")
        cur = self._conn.cursor()
        cur.execute("CREATE TABLE service_checks (signal TEXT, value)")
        cur.execute("CREATE TABLE measurements (name TEXT, value)")
        cur.execute("CREATE TABLE equations (icon TEXT, sql TEXT)")
        cur.execute(
            "INSERT INTO equations VALUES ('OIL', "
            "\"SELECT COUNT(*) FROM service_checks "
            "WHERE signal = 'service_due' AND value = 1\")"
        )
        self._conn.commit()

    def insert(self, table: str, columns: tuple, row: tuple) -> None:
        placeholders = ", ".join("?" for _ in row)
        self._conn.execute(
            "INSERT INTO %s (%s) VALUES (%s)"
            % (table, ", ".join(columns), placeholders),
            row,
        )
        self._conn.commit()

    def rows(self, table: str) -> list:
        return self._conn.execute("SELECT * FROM %s" % table).fetchall()

    def query(self, sql: str) -> list:
        return self._conn.execute(sql).fetchall()

    def equation_triggered(self, icon: str) -> bool:
        found = self._conn.execute(
            "SELECT sql FROM equations WHERE icon = ?", (icon,)
        ).fetchone()
        if found is None:
            raise KeyError("no equation for icon %r" % icon)
        return bool(self._conn.execute(found[0]).fetchone()[0])


class TableBuilder:
    """Inserts values into the HDB's tables."""

    def __init__(self, db: Hdb) -> None:
        self._db = db

    def add_service_check(self, signal: str, value: Any) -> None:
        self._db.insert("service_checks", ("signal", "value"), (signal, value))

    def add_measurement(self, name: str, value: Any) -> None:
        self._db.insert("measurements", ("name", "value"), (name, value))


class Epc:
    """EPC — electronic parts catalog (sqlite): every part and signal defined by name."""

    _PARTS = [
        ("P-001", "instrument cluster"),
        ("P-002", "powertrain control module"),
        ("P-003", "fuel system"),
        ("P-004", "wheels and tires"),
    ]
    _SIGNALS = [
        ("odometer_miles", "P-001", "mi"),
        ("last_service_miles", "P-002", "mi"),
        ("service_interval_miles", "P-002", "mi"),
        ("trip_miles", "P-001", "mi"),
        ("trip_gallons", "P-003", "gal"),
        ("tire_miles", "P-004", "mi"),
        ("tire_rated_miles", "P-004", "mi"),
    ]

    def __init__(self) -> None:
        self._conn = sqlite3.connect(":memory:")
        self._conn.execute("CREATE TABLE parts (part_no TEXT PRIMARY KEY, name TEXT)")
        self._conn.execute("CREATE TABLE signals (name TEXT PRIMARY KEY, part_no TEXT, unit TEXT)")
        self._conn.executemany("INSERT INTO parts VALUES (?, ?)", self._PARTS)
        self._conn.executemany("INSERT INTO signals VALUES (?, ?, ?)", self._SIGNALS)
        self._conn.commit()

    def signal(self, name: str) -> dict:
        row = self._conn.execute(
            "SELECT name, part_no, unit FROM signals WHERE name = ?", (name,)
        ).fetchone()
        if row is None:
            raise KeyError("signal %r not defined in EPC" % name)
        return {"name": row[0], "part_no": row[1], "unit": row[2]}

    def part(self, part_no: str) -> dict:
        row = self._conn.execute(
            "SELECT part_no, name FROM parts WHERE part_no = ?", (part_no,)
        ).fetchone()
        if row is None:
            raise KeyError("part %r not defined in EPC" % part_no)
        return {"part_no": row[0], "name": row[1]}


class CarSim:
    """CarSim (CS) — car simulation running on Windows machines."""

    def __init__(self, unit: Any, **signals: Any) -> None:
        self._unit = unit
        self._signals = signals

    def read_signal(self, signal: str) -> Any:
        return self._signals[signal]

    def unit_under_test(self) -> Any:
        return self._unit


class TestBed:
    """The test bed: drives real hardware on the rig, or a CarSim (CS) instance on Windows."""

    def __init__(self, source: CarSim, epc: Epc = None) -> None:
        self._source = source
        self._epc = epc or Epc()
        self.faults: list = []

    def read(self, signal: str) -> Any:
        self._epc.signal(signal)  # unknown signal names are a test bug, not a car fault
        return self._source.read_signal(signal)

    def unit_under_test(self) -> Any:
        return self._source.unit_under_test()

    def raise_fault(self, code: str) -> None:
        self.faults.append(code)


class HdbFactory:
    """Creates HDBs at runtime; .create(name) returns a fresh database with tables."""

    def create(self, name: str) -> Hdb:
        return Hdb(name)


def LogCollectionAndTest(
    app: Any = None,
    tp: Any = None,
    use_whitelist: bool = False,
    save_logs: bool = True,
    delete_initial_logs: bool = False,
    white_list_extention_faults: Any = None,
    white_list_extention_full_faults: Any = None,
    white_list_extention_regex_faults: Any = None,
    save_dir: Any = None,
):
    """Collects logs and checks the fault whitelist around a test item; here it just runs it."""

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator

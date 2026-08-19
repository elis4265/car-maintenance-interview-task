from typing import Any

from hil_framework import LogCollectionAndTest, TestBed, HdbFactory, TableBuilder

app = None  # Interface from API.EXE, supplied by the runner
tp = None   # supplied by the runner


@LogCollectionAndTest(app=app, tp=tp, use_whitelist=True, save_logs=True)
def run_ti_5001(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5001 — a clearly-overdue car is flagged as due and lights the OIL icon."""
    unit = test_bed.unit_under_test()
    db = hdb_factory.create("ti_5001_results")
    builder = TableBuilder(db)

    current = test_bed.read("odometer_miles")
    last = test_bed.read("last_service_miles")
    interval = test_bed.read("service_interval_miles")

    due = unit.is_service_due(current, last, interval)
    builder.add_service_check("service_due", due)

    assert due is True, f"expected service due after {current - last} miles"
    assert db.equation_triggered("OIL"), "OIL icon should light for an overdue car"


@LogCollectionAndTest(app=app, tp=tp, use_whitelist=True, save_logs=True)
def run_ti_5002(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5002 — service-due behaviour around one service interval."""
    unit = test_bed.unit_under_test()
    builder = TableBuilder(hdb_factory.create("ti_5002_results"))

    last = test_bed.read("last_service_miles")
    interval = test_bed.read("service_interval_miles")

    due_under = unit.is_service_due(last + interval - 1, last, interval)
    builder.add_service_check("due_under_interval", due_under)
    assert due_under is False, "service flagged due before a full interval"

    # at exactly one interval the car hasn't gone past it yet, so not due
    due_at = unit.is_service_due(last + interval, last, interval)
    builder.add_service_check("due_at_interval", due_at)
    assert due_at is False, "service flagged due at exactly one interval"


@LogCollectionAndTest(app=app, tp=tp, use_whitelist=True, save_logs=True)
def run_ti_5003(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5003 — fuel economy over a recorded trip."""
    unit = test_bed.unit_under_test()
    builder = TableBuilder(hdb_factory.create("ti_5003_results"))

    miles = test_bed.read("trip_miles")
    gallons = test_bed.read("trip_gallons")

    mpg = unit.average_fuel_economy(miles, gallons)
    builder.add_measurement("avg_mpg", mpg)
    assert mpg == 25.0, f"expected 25.0 mpg, got {mpg}"

    try:
        unit.average_fuel_economy(miles, 0)
    except ZeroDivisionError:
        pass  # no fuel drawn, nothing to measure


@LogCollectionAndTest(app=app, tp=tp, use_whitelist=True, save_logs=True)
def run_ti_5004(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5004 — tire wear estimate for a tire late in its life."""
    unit = test_bed.unit_under_test()
    builder = TableBuilder(hdb_factory.create("ti_5004_results"))

    tire_miles = test_bed.read("tire_miles")
    rated = test_bed.read("tire_rated_miles")

    wear = unit.estimate_tire_wear_percent(tire_miles, rated)
    builder.add_measurement("tire_wear_percent", wear)

    # this tire has done more than its rated mileage, so it's fully worn
    assert wear >= 100, f"expected a fully worn tire, got {wear}%"


@LogCollectionAndTest(app=app, tp=tp, use_whitelist=True, save_logs=True)
def run_ti_5005(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5005 — a service visit is written into the service history."""
    unit = test_bed.unit_under_test()
    builder = TableBuilder(hdb_factory.create("ti_5005_results"))

    mileage = test_bed.read("odometer_miles")
    records = unit.add_service_record(mileage, "oil change")
    builder.add_service_check("record_count", len(records))

    assert len(records) == 1, f"expected one record, got {len(records)}"
    assert records[0]["mileage"] == mileage


@LogCollectionAndTest(
    app=app,
    tp=tp,
    use_whitelist=True,
    save_logs=True,
    save_dir=r"C:\Users\jsmith\Desktop\logs_new_FINAL",
)
def run_ti_5006(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5006 — fuel economy in metric for the EU cluster display."""
    unit = test_bed.unit_under_test()
    builder = TableBuilder(hdb_factory.create("ti_5006_results"))

    miles = test_bed.read("trip_miles")
    gallons = test_bed.read("trip_gallons")

    kpl = unit.average_fuel_economy_km_per_liter(miles, gallons)
    builder.add_measurement("avg_km_per_liter", kpl)
    assert kpl > 0, f"expected a positive km/L figure, got {kpl}"


@LogCollectionAndTest(app=app, tp=tp, use_whitelist=True, save_logs=True)
def run_ti_5007(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5007 — service-due after an instrument cluster replacement."""
    unit = test_bed.unit_under_test()
    builder = TableBuilder(hdb_factory.create("ti_5007_results"))

    last = test_bed.read("last_service_miles")
    interval = test_bed.read("service_interval_miles")

    # replacement cluster starts near zero; the counter restarts, so not due
    due = unit.is_service_due(1_200, last, interval)
    builder.add_service_check("due_after_cluster_swap", due)
    assert due is False, "service flagged due right after a cluster swap"


@LogCollectionAndTest(app=app, tp=tp, use_whitelist=True, save_logs=True)
def run_ti_5008(test_bed: TestBed, hdb_factory: HdbFactory, **_: Any) -> Any:
    """TI-5008 — recorded checks can be read back from the HDB by name."""
    unit = test_bed.unit_under_test()
    db = hdb_factory.create("ti_5008_results")
    builder = TableBuilder(db)

    current = test_bed.read("odometer_miles")
    last = test_bed.read("last_service_miles")
    interval = test_bed.read("service_interval_miles")

    due = unit.is_service_due(current, last, interval)
    builder.add_service_check("service_due", due)

    # the operator types the check name into the rig UI to pull it back up
    check = "service_due"
    rows = db.query("SELECT value FROM service_checks WHERE signal = '" + check + "'")
    assert rows and rows[0][0] == 1, "recorded check not found in HDB"


# dbg: quick OIL check on CS, works without the rig
from car_maintenance import MaintenanceUnit
from hil_framework import CarSim
run_ti_5001(
    TestBed(CarSim(
        MaintenanceUnit(),
        odometer_miles=60_000,
        last_service_miles=54_000,
        service_interval_miles=5_000,
    )),
    HdbFactory(),
)

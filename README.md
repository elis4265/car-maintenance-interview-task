# Code Review Task — Car Maintenance Unit

## The PR you're reviewing

A teammate opened a pull request — *"car maintenance unit + rig test items,
all green on CS"* — and you're the assigned reviewer. If you approve, it
merges and starts gating real cars on the rig.

Some context: the car's **maintenance unit** works out whether a **service
is due**, the **fuel economy** of a trip, and how much **tire tread life**
has been used. Test items drive it through the **TestBed** — on the rig
against real hardware (HW), or attached to **CarSim (CS)**, a car simulation
running on Windows machines. Same test code either way. Every part and
signal is defined by name in the **EPC** — the **electronic parts catalog**
(sqlite). Results are stored in the **HDB** — the **historical database**
(sqlite) — whose **equations** (SQL conditions over that history) decide
when a dashboard icon like **OIL** lights up.

Changed files in the PR:

- `car_maintenance.py` — the unit under test.
- `test_car_maintenance_ti.py` — eight test items (`run_ti_*`). CI is
  green: all eight pass.
- `hil_framework.py` — a stand-in for the real framework so the PR runs
  off-hardware. Not part of the review.

## Your review

We care about **how you think**, not an exhaustive list.

1. **What would you comment on?** — with a quick *why* and *how serious*.
2. If the author could fix only **three** things before merge, which three
   and why?

No need to run or fix anything — walk us through the review out loud, then
call it: approve, or request changes.

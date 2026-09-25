# Test Drive Telemetry

A backend platform that ingests vehicle test-drive telemetry, processes it asynchronously and exposes results through a REST API and a simple web dashboard.

## Dataset

Real trip data comes from:

> Matthias Steinstraeter, Johannes Buberger, Dimitar Trifonov, "Battery and Heating Data in Real Driving Cycles," IEEE Dataport, October 19, 2020, doi: [10.21227/6jr9-5235](https://dx.doi.org/10.21227/6jr9-5235).

72 real trips of a 2014 BMW i3 (60 Ah), Munich, sampled at 10 Hz, summer and winter. Hosted on [IEEE DataPort](https://ieee-dataport.org/open-access/battery-and-heating-data-real-driving-cycles) as Open Access; the source page does not state explicit license terms beyond that, so treat it accordingly if you plan to redistribute anything beyond the small samples in `data/samples/` used for tests.

A synthetic test fleet is derived from these trips for development and demo purposes — see `scripts/generate_fleet.py` once added, and `docs/context.md` for what's real vs. synthetic.

## Status

Work in progress.

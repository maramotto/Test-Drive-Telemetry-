# Test Drive Telemetry

A backend platform that ingests vehicle test-drive telemetry, processes it asynchronously and exposes results through a REST API and a simple web dashboard. It simulates the kind of R&D data platform an automotive company runs on the cloud.

**Status:** work in progress.

## Getting started

```bash
uv sync
uv run scripts/download_dataset.py
```

## Dataset

> "Battery and Heating Data in Real Driving Cycles", Matthias Steinstraeter, Johannes Buberger, Dimitar Trifonov, Institute of Automotive Technology, Technical University of Munich (TUM). IEEE DataPort, DOI [10.21227/6jr9-5235](https://dx.doi.org/10.21227/6jr9-5235).

- Downloaded from the Kaggle mirror [`atechnohazard/battery-and-heating-data-in-real-driving-cycles`](https://www.kaggle.com/datasets/atechnohazard/battery-and-heating-data-in-real-driving-cycles), pinned to version 1 (see `scripts/download_dataset.py`).
- 70 trips of a BMW i3 (60 Ah), 10 Hz, summer and winter.
- Dataset license: Creative Commons Attribution 4.0 International (CC BY 4.0), https://creativecommons.org/licenses/by/4.0/
- The platform is OEM-agnostic; this dataset is just the first source adapter.

## License

Code in this repository is MIT licensed (see LICENSE). The dataset is
licensed CC BY 4.0 by its authors and is not included in this repository;
see the Dataset section for attribution.

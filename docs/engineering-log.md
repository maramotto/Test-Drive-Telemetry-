# Engineering log

Problems found while building this project and how they were solved, in the order they happened.

## 2026-09-25 — Dataset has 70 trips, not 72

**Problem:** the dataset abstract mentions 72 trips, but there are 70 CSV files (TripA01–A32 summer, TripB01–B38 winter).
**Cause:** `Overview.xlsx` has 72 rows, but rows 32 and 33 are empty separator rows between the summer and winter trips.
**Resolution:** documented as 70 trips; the overview loader must drop rows with no Trip.

<!-- Entry template:
## YYYY-MM-DD — Short title

**Problem:** what went wrong.
**Cause:** why it happened.
**Solution:** what fixed it.
-->

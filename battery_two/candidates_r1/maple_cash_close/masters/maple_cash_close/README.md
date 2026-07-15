# Maple Street Markets — June cash close

This directory contains the closed daily drawer-audit export for 16 stores and the retained register export profile.

- `drawer_cash_audits.csv`: one close row per drawer and date. Bill fields are counts; `coins_cents` is a dollar-independent cent amount.
- `register_export_profile.json`: configuration captured when the compact register export was scheduled.

All drawers have `CLOSED` audit status. Safe drops and bank deposits occur after the recorded daily close.

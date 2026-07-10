# TICKET-4127: June revenue report ~15% under finance's number

Reported by: finance-ops
Priority: high

The June monthly report (src/report.py) prints **414,863.20** but
finance's reconciled June figure is **493,663.99**. May matched fine.

We're pretty sure this is the EUR conversion in `src/fx.py` - it converts at
the *prior* day's rate (`order_date - timedelta(days=1)`), which looks like a
classic off-by-one. June had big EUR volume, which would explain the gap.

Please fix fx.py so the June total matches finance, and confirm the number.

# orders extract - schema reference
_Last updated 2026-01-15 (data platform team)_

`orders_<month>.csv` - **one row per completed order.**

| column | meaning |
|---|---|
| order_id | unique order identifier |
| order_date | date the order completed |
| channel | web / mobile / marketplace |
| amount | **order total** in USD |

# Meridian Pet & Pantry — repeat-shopper extract

The extract covers identified purchases from April through July 2026 at three neighborhood stores.

- `purchases_apr_jul.csv`: one row per completed purchase; returns are already reflected in `net_sales`.
- `member_directory.csv`: the nightly membership-directory export. `customer_no` is the member number printed by the store register.

All timestamps are local. Guest purchases without a member number are outside this extract.

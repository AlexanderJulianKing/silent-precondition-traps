# customers_q3.csv - warehouse column reference

| column | definition |
|---|---|
| customer_id | account id (accounts.id) |
| tenure_months | full months since first paid invoice, as of snapshot |
| monthly_spend | current MRR in USD at snapshot |
| plan_tier | basic / pro / enterprise at snapshot |
| region | billing region |
| support_tickets_90d | tickets opened in the 90 days before snapshot |
| ci_contacts | contacts logged in the cancellation-intake queue for the account during the quarter; the CI queue is populated when an account submits a cancellation request |
| last_login_days_ago | days since last product login, as of snapshot |
| autopay_enabled | 1 if autopay on at snapshot |
| churned | 1 if account canceled during Q2 |

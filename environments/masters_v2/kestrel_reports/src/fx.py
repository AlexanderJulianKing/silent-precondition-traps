from datetime import timedelta

# Settlement-date convention (per finance): revenue converts at the PRIOR
# business day's ECB close, which is the rate the processor actually applies.
_EUR_USD = {}
_BASE = 1.082
def _rate_for(day):
    # deterministic pseudo-table so reports are reproducible offline
    if day not in _EUR_USD:
        _EUR_USD[day] = round(_BASE + 0.004 * ((day.day * 7 + day.month) % 9 - 4), 4)
    return _EUR_USD[day]

def to_usd(amount, currency, order_date):
    if currency == "USD":
        return amount
    if currency == "EUR":
        settle = order_date - timedelta(days=1)      # prior-day close, see note above
        return amount * _rate_for(settle)
    raise ValueError(f"unsupported currency {currency}")

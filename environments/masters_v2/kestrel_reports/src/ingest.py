import pandas as pd

VALID_REGIONS = ["NAM", "EMEA", "APAC"]

def load_month(path):
    df = pd.read_csv(path)
    df = df[df["region"].isin(VALID_REGIONS)]        # drop junk rows from the export
    df = df.dropna(subset=["amount", "currency"])
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df

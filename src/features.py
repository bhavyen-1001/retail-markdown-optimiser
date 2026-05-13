import pandas as pd
import numpy as np

def build_features(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Adds log_price, iso_week_number, and is_q4 columns to the
    transaction-level DataFrame.

    Args:
        df: Cleaned, categorised DataFrame from product_categorisation.py.

    Returns:
        DataFrame with three additional columns.
    """
    df = df_input.copy()
    
    df['log_price'] = np.log(df['UnitPrice'])
    df['iso_week_number'] = df['InvoiceDate'].dt.isocalendar().week
    df['is_q4'] = df['iso_week_number'].between(40, 52).astype(int)
    
    return df
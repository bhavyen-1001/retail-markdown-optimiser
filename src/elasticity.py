import pandas as pd
import numpy as np

def aggregate_weekly_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregates transaction data to the weekly level per segment.
    Filters out segments with insufficient data for elasticity modelling.

    Args:
        df: Transaction-level DataFrame.

    Returns:
        DataFrame aggregated to the segment-week level.
    """
    weekly = (
        df.groupby(['segment', 'year', 'week'])
        .agg(
            weekly_qty=('Quantity', 'sum'),
            unit_price=('UnitPrice', 'median'),
            week_number=('week', 'first')
        )
        .reset_index()
    )

    weekly['log_qty'] = np.log(weekly['weekly_qty'])
    weekly['log_price'] = np.log(weekly['unit_price'])
    weekly['is_q4'] = weekly['week_number'].between(40, 52).astype(int)

    # Filter segments based on modelling requirements
    segment_counts = weekly.groupby('segment').size()
    segment_prices = weekly.groupby('segment')['unit_price'].nunique()

    valid_segments = segment_counts[
        (segment_counts >= 30) & (segment_prices >= 2)
    ].index

    dropped_segments = set(weekly['segment'].unique()) - set(valid_segments)
    if dropped_segments:
        print(f"Dropped {len(dropped_segments)} segments due to insufficient data (<30 obs or <2 price points).")

    return weekly[weekly['segment'].isin(valid_segments)].copy()
import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Cleans the raw retail dataset by removing anomalies, returns, and non-product codes.
    Also engineers base features like Revenue and ISO week.
    
    Args:
        df (pd.DataFrame): The raw Kaggle retail dataset.
        
    Returns:
        pd.DataFrame: The cleaned dataset ready for EDA and modelling.
    """
    
    df_clean = df.copy()
    
    # 1. Remove Cancellations & Returns
    df_clean = df_clean[~df_clean['Invoice'].astype(str).str.startswith('C')]
    df_clean = df_clean[df_clean['Quantity'] > 0]
    
    # 2. Removing Price <= 0
    df_clean = df_clean[df_clean['Price'] > 0]
    
    # 3. Removing non-product Stock Codes
    valid_pattern = r'^\d{5}[a-zA-Z]?$'
    df_clean = df_clean[df_clean['StockCode'].astype(str).str.strip().str.match(valid_pattern)]
    
    # 4. Cleaning Missing/Invalid Descriptions
    invalid_desc_mask = df_clean['Description'].isna() | df_clean['Description'].str.contains('?', regex=False, na=False)
    df_clean = df_clean[~invalid_desc_mask]
    
    # 5. Removing Non-UK Transactions
    df_clean = df_clean[df_clean['Country'] == 'United Kingdom']
    
    # 6. Base Feature Extraction
    df_clean['InvoiceDate'] = pd.to_datetime(df_clean['InvoiceDate'])
    df_clean['date'] = df_clean['InvoiceDate'].dt.date
    df_clean['year'] = df_clean['InvoiceDate'].dt.year
    df_clean['month'] = df_clean['InvoiceDate'].dt.month
    df_clean['week'] = df_clean['InvoiceDate'].dt.isocalendar().week
    df_clean['Revenue'] = df_clean['Quantity'] * df_clean['Price']
    
    return df_clean
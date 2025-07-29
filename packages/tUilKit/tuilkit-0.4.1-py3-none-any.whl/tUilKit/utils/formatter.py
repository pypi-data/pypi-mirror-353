import json

def load_column_widths():
    """Loads predefined column widths from JSON configuration."""
    with open("tUilKit/config/COLUMN_WIDTHS.json", "r") as file:
        return json.load(file)

def apply_column_format(df):
    """Applies width and formatting rules to dataframe columns."""
    column_widths = load_column_widths()
    for col in df.columns:
        if col in column_widths:
            df[col] = df[col].apply(lambda x: str(x).ljust(column_widths[col]))  # Apply width padding
    return df  
import pandas as pd
import json
import hashlib
import os
from itertools import combinations
from fuzzywuzzy import fuzz
from tUilKit.interfaces.df_interface import DataFrameInterface
from tUilKit.config.config import ConfigLoader

def hash_row(row, columns):
    """Creates a consistent hash for a row, regardless of column order."""
    sorted_values = [str(row[col]) for col in sorted(columns)]
    row_str = ','.join(sorted_values)
    return hashlib.sha256(row_str.encode()).hexdigest()

def smart_diff(df1, df2):
    """Compares two dataframes irrespective of row order."""
    common_cols = find_common_columns([df1, df2])
    df1 = df1.copy()
    df2 = df2.copy()
    df1['row_hash'] = df1.apply(lambda row: hash_row(row, common_cols), axis=1)
    df2['row_hash'] = df2.apply(lambda row: hash_row(row, common_cols), axis=1)
    changed_rows = df1.loc[~df1['row_hash'].isin(df2['row_hash'])]
    return changed_rows

def find_fuzzy_columns(df_list):
    """Detects columns with similar data patterns across multiple dataframes using fuzzy matching."""
    common_columns = set(df_list[0].columns)
    for df in df_list[1:]:
        potential_matches = set()
        for col1 in common_columns:
            for col2 in df.columns:
                # Join values to a single string for fuzzy comparison
                s1 = " ".join(df_list[0][col1].astype(str).tolist())
                s2 = " ".join(df[col2].astype(str).tolist())
                match_score = fuzz.partial_ratio(s1, s2)
                if match_score > 80:
                    potential_matches.add(col1)
        common_columns = common_columns.intersection(potential_matches)
    return list(common_columns)

def find_common_columns(df_list):
    """Finds strictly matching columns (by name) across all dataframes."""
    common_columns = set(df_list[0].columns)
    for df in df_list[1:]:
        common_columns = common_columns.intersection(df.columns)
    return list(common_columns)

def find_composite_keys(df1, df2):
    """Identify potential composite keys when single keys don’t exist."""
    common_cols = list(set(df1.columns) & set(df2.columns))
    best_combo = None
    best_match = 0
    for i in range(1, len(common_cols) + 1):
        for combo in combinations(common_cols, i):
            merged = pd.merge(df1, df2, on=list(combo), how='inner')
            match_score = len(merged) / min(len(df1), len(df2)) if min(len(df1), len(df2)) > 0 else 0
            if match_score > best_match:
                best_match = match_score
                best_combo = list(combo)
    return best_combo if best_combo else common_cols

def load_column_mapping(config_loader=None):
    """Loads column mapping from JSON configuration using ConfigLoader."""
    if config_loader is None:
        config_loader = ConfigLoader()
    # Try to get the mapping path using config loader
    mapping_path = config_loader.get_json_path('COLUMN_MAPPING.json')
    with open(mapping_path, "r") as file:
        mapping_json = json.load(file)
        # Support both {"COLUMN_MAPPING": {...}} and flat {...}
        if "COLUMN_MAPPING" in mapping_json:
            return mapping_json["COLUMN_MAPPING"]
        return mapping_json

def smart_merge(df_list, merge_type="outer", config_loader=None):
    """Merges multiple dataframes intelligently with column mapping."""
    col_mapping = load_column_mapping(config_loader)
    df_list = [df.rename(columns=col_mapping) for df in df_list]
    return pd.concat(df_list, axis=0, ignore_index=True, join=merge_type)

# DataFrame handler using the interface
class SmartDataFrameHandler(DataFrameInterface):
    def merge(self, df_list, merge_type="outer", config_loader=None):
        return smart_merge(df_list, merge_type, config_loader=config_loader)
    def compare(self, df1, df2):
        return smart_diff(df1, df2)
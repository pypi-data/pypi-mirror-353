from abc import ABC, abstractmethod 
import pandas as pd

class DataFrameInterface(ABC):
    """Abstract interface for intelligent dataframe handling."""

    @abstractmethod
    def merge(self, df_list, merge_type="outer"):
        """Merges multiple dataframes intelligently."""
        pass

    @abstractmethod
    def compare(self, df1, df2):
        """Compares two dataframes while handling inconsistencies."""
        pass

class SmartDataFrameHandler(DataFrameInterface):
    """Implements smart dataframe logic including fuzzy matching."""

    def merge(self, df_list, merge_type="outer", config_loader=None):
        return smart_merge(df_list, merge_type)

    def compare(self, df1, df2):
        return smart_diff(df1, df2)

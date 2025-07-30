"""
Hygiea: Your Data's New Superpower

A comprehensive Python toolkit for data cleaning and preprocessing.

Key Features:
- Standardize column names and auto-detect data types
- Advanced imputation methods (median, KNN, MICE)
- Outlier detection and winsorization
- Multiple encoding strategies
- Comprehensive EDA and profiling
- Time series and text analysis
- Scikit-learn pipeline compatibility

Quick Start:
    >>> import hygiea as hg
    >>> df_clean = hg.clean_data(df)
    >>> hg.profile_data(df, 'report.html')
"""

from .__version__ import __version__

# Core functionality
from .core.standardizer import HygieaStandardizer

# Main class
from .hygiea import Hygiea

# Convenience functions
from .api import clean_data, profile_data, get_transformer, suggest_cleaning_strategy, quick_clean

__all__ = [
    '__version__',
    'Hygiea',
    'HygieaStandardizer',
    'clean_data',
    'profile_data',
    'get_transformer',
    'suggest_cleaning_strategy',
    'quick_clean',
]

# Package metadata
__author__ = 'Hygiea Development Team'
__email__ = 'hygiea@example.com'
__license__ = 'MIT'
__description__ = 'A comprehensive Python toolkit for data cleaning and preprocessing'

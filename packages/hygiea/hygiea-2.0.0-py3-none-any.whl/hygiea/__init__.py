"""
Hygiea: Your Data's New Superpower

A comprehensive Python toolkit for data cleaning and preprocessing with
advanced imputation capabilities and CLI interface.

Key Features:
- Standardize column names and auto-detect data types
- Advanced imputation methods (median, KNN, MICE, custom functions)
- Outlier detection and winsorization
- Multiple encoding strategies
- Comprehensive EDA and profiling
- Time series and text analysis
- Scikit-learn pipeline compatibility
- Complete CLI interface
- Custom imputation function support

Quick Start:
    >>> import hygiea as hg
    >>> df_clean = hg.clean_data(df)
    >>> hg.profile_data(df, 'report.html')
    
CLI Usage:
    $ hygiea clean data.csv --output clean_data.csv
    $ hygiea profile data.csv --output report.html
"""

from .__version__ import __version__

# Core functionality
from .core.standardizer import HygieaStandardizer
from .imputation.imputer import CustomImputer, ImputationStrategy

# Main class
from .hygiea import Hygiea

# Convenience functions
from .api import (
    clean_data, 
    profile_data, 
    get_transformer, 
    suggest_cleaning_strategy, 
    quick_clean,
    analyze_data
)

__all__ = [
    '__version__',
    'Hygiea',
    'HygieaStandardizer',
    'CustomImputer',
    'ImputationStrategy',
    'clean_data',
    'profile_data',
    'get_transformer',
    'suggest_cleaning_strategy',
    'quick_clean',
    'analyze_data',
]

# Package metadata
__author__ = 'Hygiea Development Team'
__email__ = 'hygiea@example.com'
__license__ = 'MIT'
__description__ = 'A comprehensive Python toolkit for data cleaning and preprocessing with CLI'

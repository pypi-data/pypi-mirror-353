"""Convenience API functions for quick access to Hygiea functionality."""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any
from .hygiea import Hygiea


def clean_data(
    df: pd.DataFrame, 
    profile: str = 'default',
    custom_config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Quick data cleaning function.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    profile : str, default='default'
        Cleaning profile: 'default', 'aggressive', 'gentle', 'minimal', 'custom'
    custom_config : dict, optional
        Custom configuration for 'custom' profile
        
    Returns
    -------
    pd.DataFrame
        Cleaned dataframe
        
    Examples
    --------
    >>> import hygiea as hg
    >>> df_clean = hg.clean_data(df, profile='aggressive')
    """
    hygiea = Hygiea()
    return hygiea.clean_data(df, profile=profile, custom_config=custom_config)


def profile_data(
    df: pd.DataFrame,
    title: str = "Data Profile Report",
    output_file: Optional[str] = None
) -> str:
    """
    Quick profiling function to generate HTML reports.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    title : str, default="Data Profile Report"
        Report title
    output_file : str, optional
        Output HTML file path
        
    Returns
    -------
    str
        HTML report content
        
    Examples
    --------
    >>> import hygiea as hg
    >>> hg.profile_data(df, output_file='report.html')
    """
    hygiea = Hygiea()
    return hygiea.quick_profile(df, title=title, output_file=output_file)


def get_transformer(**kwargs):
    """Get sklearn-compatible transformer for pipeline integration."""
    from sklearn.base import BaseEstimator, TransformerMixin
    
    class HygieaTransformer(BaseEstimator, TransformerMixin):
        """Sklearn-compatible transformer for Hygiea cleaning."""
        
        def __init__(self, profile='default', **clean_params):
            self.profile = profile
            self.clean_params = clean_params
            self.hygiea = Hygiea()
        
        def fit(self, X, y=None):
            """Fit the transformer (no-op for now)."""
            return self
        
        def transform(self, X):
            """Transform the data using Hygiea cleaning."""
            if isinstance(X, np.ndarray):
                # Convert numpy array to DataFrame
                X = pd.DataFrame(X)
            
            return self.hygiea.clean_data(X, profile=self.profile, **self.clean_params)
    
    return HygieaTransformer(**kwargs)


def suggest_cleaning_strategy(df: pd.DataFrame) -> Dict[str, Any]:
    """Analyze data and suggest optimal cleaning strategy."""
    # Analyze data characteristics
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    duplicates = df.duplicated().sum()
    duplicate_pct = (duplicates / len(df)) * 100
    
    # Count columns with potential issues
    messy_columns = 0
    for col in df.columns:
        col_str = str(col)
        if any(char in col_str for char in [' ', '(', ')', '$', '?', '#']):
            messy_columns += 1
    
    # Count outliers in numeric columns
    outlier_columns = 0
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if len(numeric_cols) > 0:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.05:  # More than 5% outliers
                outlier_columns += 1
    
    suggestions = {
        'recommended_profile': 'default',
        'rationale': [],
        'warnings': [],
        'estimated_impact': {}
    }
    
    # Determine recommended profile
    if missing_pct > 30 or outlier_columns > len(numeric_cols) * 0.5:
        suggestions['recommended_profile'] = 'aggressive'
        suggestions['rationale'].append(f"High missing data ({missing_pct:.1f}%) or many outliers")
    elif missing_pct < 5 and messy_columns == 0 and duplicate_pct < 1:
        suggestions['recommended_profile'] = 'gentle'
        suggestions['rationale'].append("Data is relatively clean - gentle cleaning sufficient")
    else:
        suggestions['recommended_profile'] = 'default'
        suggestions['rationale'].append("Standard cleaning recommended for typical data issues")
    
    # Add specific observations
    if missing_pct > 10:
        suggestions['rationale'].append(f"Missing data: {missing_pct:.1f}% of cells are empty")
    
    if duplicate_pct > 5:
        suggestions['warnings'].append(f"High duplicate rate: {duplicate_pct:.1f}% duplicate rows")
    
    if messy_columns > 0:
        suggestions['rationale'].append(f"Column naming issues: {messy_columns} columns need standardization")
    
    if outlier_columns > 0:
        suggestions['rationale'].append(f"Outlier issues: {outlier_columns} columns have significant outliers")
    
    # Estimate impact
    suggestions['estimated_impact'] = {
        'missing_reduction': f"{missing_pct:.1f}% → 0%",
        'column_standardization': f"{messy_columns} columns will be cleaned",
        'data_quality_improvement': "Expected 20-40% improvement in data quality",
        'memory_optimization': "Potential 10-30% memory reduction"
    }
    
    return suggestions


def quick_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Ultra-quick cleaning with smart defaults."""
    suggestions = suggest_cleaning_strategy(df)
    recommended_profile = suggestions['recommended_profile']
    
    return clean_data(df, profile=recommended_profile)


def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Comprehensive data analysis and quality assessment."""
    analysis = {}
    
    # Basic info
    analysis['shape'] = df.shape
    analysis['memory_usage_mb'] = df.memory_usage(deep=True).sum() / 1024**2
    
    # Missing data analysis
    missing_count = df.isnull().sum().sum()
    analysis['missing_count'] = missing_count
    analysis['missing_percentage'] = (missing_count / (len(df) * len(df.columns))) * 100
    
    # Data types
    analysis['dtypes'] = df.dtypes.value_counts().to_dict()
    
    # Duplicates
    analysis['duplicate_rows'] = df.duplicated().sum()
    analysis['duplicate_percentage'] = (analysis['duplicate_rows'] / len(df)) * 100
    
    # Column analysis
    analysis['columns'] = {
        'total': len(df.columns),
        'numeric': len(df.select_dtypes(include=[np.number]).columns),
        'categorical': len(df.select_dtypes(include=['object', 'category']).columns),
        'datetime': len(df.select_dtypes(include=['datetime']).columns)
    }
    
    # Quality score calculation
    completeness = 1 - (missing_count / (len(df) * len(df.columns)))
    uniqueness = 1 - (analysis['duplicate_rows'] / len(df))
    
    # Consistency score (simple heuristic)
    consistency = 1.0  # Start with perfect consistency
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check for mixed types (numbers stored as strings)
            try:
                numeric_conversion = pd.to_numeric(df[col].dropna(), errors='coerce')
                if numeric_conversion.notna().sum() > 0.5 * len(df[col].dropna()):
                    consistency -= 0.1  # Penalty for likely numeric data stored as object
            except:
                pass
    
    consistency = max(0, consistency)
    
    analysis['quality_score'] = (completeness * 0.4 + uniqueness * 0.3 + consistency * 0.3) * 100
    analysis['completeness'] = completeness * 100
    analysis['uniqueness'] = uniqueness * 100
    analysis['consistency'] = consistency * 100
    
    return analysis

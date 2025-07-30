"""Enhanced convenience API functions with custom imputation support."""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Callable
from .hygiea import Hygiea
from .imputation.imputer import create_domain_specific_imputer, create_business_imputer


def clean_data(
    df: pd.DataFrame, 
    profile: str = 'default',
    custom_config: Optional[Dict[str, Any]] = None
) -> pd.DataFrame:
    """
    Enhanced quick data cleaning function with custom imputation support.
    
    Parameters
    ----------
    df : pd.DataFrame
        Input dataframe
    profile : str, default='default'
        Cleaning profile: 'default', 'aggressive', 'gentle', 'minimal', 'custom',
                         'research', 'financial'
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
    
    >>> # Custom imputation
    >>> def my_imputer(series):
    ...     return series.fillna(series.median() * 0.8)
    >>> config = {'custom_imputers': {'revenue': my_imputer}}
    >>> df_clean = hg.clean_data(df, profile='custom', custom_config=config)
    """
    hygiea = Hygiea()
    return hygiea.clean_data(df, profile=profile, custom_config=custom_config)


def profile_data(
    df: pd.DataFrame,
    title: str = "Data Profile Report",
    output_file: Optional[str] = None
) -> str:
    """
    Enhanced profiling function to generate beautiful HTML reports.
    
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
    """Get enhanced sklearn-compatible transformer for pipeline integration."""
    from sklearn.base import BaseEstimator, TransformerMixin
    
    class HygieaTransformer(BaseEstimator, TransformerMixin):
        """Enhanced sklearn-compatible transformer for Hygiea cleaning."""
        
        def __init__(self, profile='default', custom_config=None, **clean_params):
            self.profile = profile
            self.custom_config = custom_config or {}
            self.clean_params = clean_params
            self.hygiea = Hygiea()
        
        def fit(self, X, y=None):
            """Fit the transformer (no-op for now)."""
            return self
        
        def transform(self, X):
            """Transform the data using enhanced Hygiea cleaning."""
            if isinstance(X, np.ndarray):
                # Convert numpy array to DataFrame
                X = pd.DataFrame(X)
            
            # Merge custom_config with clean_params
            config = {**self.custom_config, **self.clean_params}
            
            if config:
                return self.hygiea.clean_data(X, profile='custom', custom_config=config)
            else:
                return self.hygiea.clean_data(X, profile=self.profile)
    
    return HygieaTransformer(**kwargs)


def suggest_cleaning_strategy(df: pd.DataFrame) -> Dict[str, Any]:
    """Enhanced analysis and suggestion of optimal cleaning strategy."""
    # Analyze data characteristics
    missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
    duplicates = df.duplicated().sum()
    duplicate_pct = (duplicates / len(df)) * 100
    
    # Count columns with potential issues
    messy_columns = 0
    for col in df.columns:
        col_str = str(col)
        if any(char in col_str for char in [' ', '(', ')', ', '?', '#']):
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
    
    # Detect data domain
    domain_indicators = {
        'financial': ['price', 'amount', 'revenue', 'cost', 'value', 'dollar', 'profit'],
        'medical': ['patient', 'treatment', 'diagnosis', 'medication', 'blood', 'heart'],
        'research': ['participant', 'survey', 'response', 'study', 'experiment'],
        'iot': ['sensor', 'temperature', 'humidity', 'battery', 'device', 'reading']
    }
    
    detected_domain = None
    for domain, keywords in domain_indicators.items():
        col_text = ' '.join(df.columns).lower()
        if sum(1 for keyword in keywords if keyword in col_text) >= 2:
            detected_domain = domain
            break
    
    suggestions = {
        'recommended_profile': 'default',
        'recommended_imputation': 'median',
        'detected_domain': detected_domain,
        'rationale': [],
        'warnings': [],
        'estimated_impact': {},
        'cli_command': ''
    }
    
    # Determine recommended profile and imputation
    if missing_pct > 40 or outlier_columns > len(numeric_cols) * 0.5:
        suggestions['recommended_profile'] = 'aggressive'
        suggestions['recommended_imputation'] = 'knn'
        suggestions['rationale'].append(f"High missing data ({missing_pct:.1f}%) or many outliers - aggressive cleaning needed")
    elif missing_pct > 20:
        suggestions['recommended_profile'] = 'default'
        suggestions['recommended_imputation'] = 'mice'
        suggestions['rationale'].append(f"Moderate missing data ({missing_pct:.1f}%) - MICE imputation recommended")
    elif missing_pct < 5 and messy_columns == 0 and duplicate_pct < 1:
        suggestions['recommended_profile'] = 'gentle'
        suggestions['recommended_imputation'] = 'median'
        suggestions['rationale'].append("Data is relatively clean - gentle cleaning sufficient")
    else:
        suggestions['recommended_profile'] = 'default'
        suggestions['recommended_imputation'] = 'median'
        suggestions['rationale'].append("Standard cleaning recommended for typical data issues")
    
    # Domain-specific recommendations
    if detected_domain:
        if detected_domain == 'financial':
            suggestions['recommended_profile'] = 'financial'
            suggestions['recommended_imputation'] = 'ffill'
            suggestions['rationale'].append(f"Financial data detected - using {detected_domain} profile with forward-fill")
        elif detected_domain == 'research':
            suggestions['recommended_profile'] = 'research'
            suggestions['recommended_imputation'] = 'mean'
            suggestions['rationale'].append(f"Research data detected - preserving missingness patterns")
        elif detected_domain in ['medical', 'iot']:
            suggestions['recommended_imputation'] = 'interpolate'
            suggestions['rationale'].append(f"{detected_domain.title()} data detected - using interpolation")
    
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
        'data_quality_improvement': "Expected 20-50% improvement in data quality",
        'memory_optimization': "Potential 10-30% memory reduction",
        'imputation_method': f"Using {suggestions['recommended_imputation']} imputation"
    }
    
    # Generate CLI command
    cmd_parts = ['hygiea', 'clean', 'your_data.csv']
    cmd_parts.extend(['--profile', suggestions['recommended_profile']])
    cmd_parts.extend(['--impute-method', suggestions['recommended_imputation']])
    
    if outlier_columns > 0:
        cmd_parts.append('--handle-outliers')
    
    if detected_domain:
        cmd_parts.extend(['--domain', detected_domain])
    
    cmd_parts.extend(['--output', 'cleaned_data.csv'])
    suggestions['cli_command'] = ' '.join(cmd_parts)
    
    return suggestions


def quick_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Ultra-quick cleaning with smart defaults and auto-detected imputation."""
    suggestions = suggest_cleaning_strategy(df)
    recommended_profile = suggestions['recommended_profile']
    recommended_imputation = suggestions['recommended_imputation']
    detected_domain = suggestions['detected_domain']
    
    # Build custom config for optimal cleaning
    if recommended_profile == 'custom' or detected_domain:
        custom_config = {
            'standardize_columns': True,
            'convert_types': True,
            'impute': True,
            'impute_method': recommended_imputation,
            'handle_outliers': True if 'outlier' in ' '.join(suggestions['rationale']) else False
        }
        
        if detected_domain:
            domain_imputer = create_domain_specific_imputer(detected_domain)
            custom_config['custom_imputers'] = {'default': domain_imputer}
        
        return clean_data(df, profile='custom', custom_config=custom_config)
    else:
        return clean_data(df, profile=recommended_profile)


def analyze_data(df: pd.DataFrame) -> Dict[str, Any]:
    """Enhanced comprehensive data analysis and quality assessment."""
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
        'datetime': len(df.select_dtypes(include=['datetime']).columns),
        'boolean': len(df.select_dtypes(include=['bool']).columns)
    }
    
    # Enhanced quality metrics
    completeness = 1 - (missing_count / (len(df) * len(df.columns)))
    uniqueness = 1 - (analysis['duplicate_rows'] / len(df))
    
    # Consistency score (enhanced)
    consistency = 1.0
    mixed_type_penalty = 0
    format_consistency_penalty = 0
    
    for col in df.columns:
        if df[col].dtype == 'object':
            # Check for mixed types
            try:
                numeric_conversion = pd.to_numeric(df[col].dropna(), errors='coerce')
                if 0.1 < numeric_conversion.notna().sum() / len(df[col].dropna()) < 0.9:
                    mixed_type_penalty += 0.1
            except:
                pass
            
            # Check format consistency for text data
            if len(df[col].dropna()) > 0:
                lengths = df[col].dropna().astype(str).str.len()
                if lengths.std() > lengths.mean() * 0.5:  # High variance in length
                    format_consistency_penalty += 0.05
    
    consistency = max(0, consistency - mixed_type_penalty - format_consistency_penalty)
    
    # Outlier analysis
    outlier_columns = 0
    total_outliers = 0
    for col in df.select_dtypes(include=[np.number]).columns:
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
        total_outliers += outliers
        if outliers > len(df) * 0.05:
            outlier_columns += 1
    
    analysis['outliers'] = {
        'columns_with_outliers': outlier_columns,
        'total_outliers': total_outliers,
        'outlier_percentage': (total_outliers / len(df)) * 100 if len(df) > 0 else 0
    }
    
    # Calculate final quality score
    outlier_factor = 1 - min(0.3, analysis['outliers']['outlier_percentage'] / 100)
    analysis['quality_score'] = (completeness * 0.4 + uniqueness * 0.3 + consistency * 0.2 + outlier_factor * 0.1) * 100
    analysis['completeness'] = completeness * 100
    analysis['uniqueness'] = uniqueness * 100
    analysis['consistency'] = consistency * 100
    
    # Data health indicators
    analysis['health_indicators'] = {
        'excellent': analysis['quality_score'] >= 90,
        'good': 70 <= analysis['quality_score'] < 90,
        'fair': 50 <= analysis['quality_score'] < 70,
        'poor': analysis['quality_score'] < 50
    }
    
    return analysis


def create_custom_imputer(
    imputation_rules: Dict[str, str],
    fallback_strategy: str = 'median'
) -> Callable:
    """
    Create a custom imputation function based on column-specific rules.
    
    Parameters
    ----------
    imputation_rules : dict
        Dictionary mapping column patterns to imputation strategies
    fallback_strategy : str, default='median'
        Fallback strategy for unmatched columns
        
    Returns
    -------
    Callable
        Custom imputation function
        
    Examples
    --------
    >>> rules = {
    ...     'revenue': 'median',
    ...     'email': 'fixed:unknown@company.com',
    ...     'rating': 'mode'
    ... }
    >>> imputer_func = create_custom_imputer(rules)
    """
    def custom_imputer(series: pd.Series) -> pd.Series:
        col_name = series.name.lower()
        
        # Check for matching rules
        for pattern, strategy in imputation_rules.items():
            if pattern.lower() in col_name:
                if strategy == 'median':
                    return series.fillna(series.median())
                elif strategy == 'mode':
                    mode_val = series.mode()
                    return series.fillna(mode_val[0] if not mode_val.empty else 'unknown')
                elif strategy == 'mean':
                    return series.fillna(series.mean())
                elif strategy.startswith('fixed:'):
                    value = strategy.split(':', 1)[1]
                    return series.fillna(value)
                elif strategy == 'interpolate':
                    return series.interpolate().fillna(method='bfill')
        
        # Fallback strategy
        if fallback_strategy == 'median':
            return series.fillna(series.median() if pd.api.types.is_numeric_dtype(series) else series.mode()[0])
        elif fallback_strategy == 'mode':
            mode_val = series.mode()
            return series.fillna(mode_val[0] if not mode_val.empty else 'unknown')
        else:
            return series.fillna(series.median() if pd.api.types.is_numeric_dtype(series) else 'unknown')
    
    return custom_imputer

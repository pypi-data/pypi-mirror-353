"""
Custom imputation strategies and utilities.
"""

import pandas as pd
import numpy as np
from typing import Callable, Dict, Any, Optional, Union
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.impute import KNNImputer
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import IterativeImputer


class ImputationStrategy:
    """Define imputation strategies and custom functions."""
    
    MEDIAN = 'median'
    MODE = 'mode'
    MEAN = 'mean'
    KNN = 'knn'
    MICE = 'mice'
    FORWARD_FILL = 'ffill'
    BACKWARD_FILL = 'bfill'
    INTERPOLATE = 'interpolate'
    CUSTOM = 'custom'
    
    @staticmethod
    def get_available_strategies():
        """Get list of available imputation strategies."""
        return [
            ImputationStrategy.MEDIAN,
            ImputationStrategy.MODE,
            ImputationStrategy.MEAN,
            ImputationStrategy.KNN,
            ImputationStrategy.MICE,
            ImputationStrategy.FORWARD_FILL,
            ImputationStrategy.BACKWARD_FILL,
            ImputationStrategy.INTERPOLATE,
            ImputationStrategy.CUSTOM
        ]


class CustomImputer(BaseEstimator, TransformerMixin):
    """
    Advanced imputer with support for custom imputation functions.
    
    Parameters
    ----------
    strategy : str, default='median'
        Imputation strategy to use
    custom_imputers : dict, optional
        Dictionary mapping column names to custom imputation functions
    default_numeric_strategy : str, default='median'
        Default strategy for numeric columns
    default_categorical_strategy : str, default='mode'
        Default strategy for categorical columns
    knn_neighbors : int, default=5
        Number of neighbors for KNN imputation
    mice_max_iter : int, default=10
        Maximum iterations for MICE imputation
    preserve_na_categories : bool, default=False
        Whether to preserve NA as a category for categorical data
    create_missingness_indicators : bool, default=False
        Whether to create binary indicators for missingness
    """
    
    def __init__(
        self,
        strategy: str = 'median',
        custom_imputers: Optional[Dict[str, Callable]] = None,
        default_numeric_strategy: str = 'median',
        default_categorical_strategy: str = 'mode',
        knn_neighbors: int = 5,
        mice_max_iter: int = 10,
        preserve_na_categories: bool = False,
        create_missingness_indicators: bool = False
    ):
        self.strategy = strategy
        self.custom_imputers = custom_imputers or {}
        self.default_numeric_strategy = default_numeric_strategy
        self.default_categorical_strategy = default_categorical_strategy
        self.knn_neighbors = knn_neighbors
        self.mice_max_iter = mice_max_iter
        self.preserve_na_categories = preserve_na_categories
        self.create_missingness_indicators = create_missingness_indicators
        
        # Fitted attributes
        self.statistics_ = {}
        self.knn_imputer_ = None
        self.mice_imputer_ = None
        self.columns_ = None
        self.dtypes_ = None
        
    def fit(self, X: pd.DataFrame, y=None):
        """
        Fit the imputer on training data.
        
        Parameters
        ----------
        X : pd.DataFrame
            Training data
        y : array-like, optional
            Target values (ignored)
            
        Returns
        -------
        self : CustomImputer
            Fitted imputer
        """
        X = self._validate_input(X)
        self.columns_ = X.columns.tolist()
        self.dtypes_ = X.dtypes.to_dict()
        
        # Fit statistics for basic strategies
        for col in X.columns:
            if col in self.custom_imputers:
                # Custom imputation - no fitting needed
                continue
                
            strategy = self._get_column_strategy(X[col])
            
            if strategy == ImputationStrategy.MEDIAN:
                self.statistics_[col] = X[col].median()
            elif strategy == ImputationStrategy.MODE:
                mode_val = X[col].mode()
                self.statistics_[col] = mode_val[0] if not mode_val.empty else None
            elif strategy == ImputationStrategy.MEAN:
                self.statistics_[col] = X[col].mean()
        
        # Fit KNN imputer if needed
        if (self.strategy == ImputationStrategy.KNN or 
            any(self._get_column_strategy(X[col]) == ImputationStrategy.KNN for col in X.columns)):
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                self.knn_imputer_ = KNNImputer(n_neighbors=self.knn_neighbors)
                self.knn_imputer_.fit(X[numeric_cols])
        
        # Fit MICE imputer if needed
        if (self.strategy == ImputationStrategy.MICE or 
            any(self._get_column_strategy(X[col]) == ImputationStrategy.MICE for col in X.columns)):
            numeric_cols = X.select_dtypes(include=[np.number]).columns
            if len(numeric_cols) > 0:
                self.mice_imputer_ = IterativeImputer(max_iter=self.mice_max_iter, random_state=42)
                self.mice_imputer_.fit(X[numeric_cols])
        
        return self
    
    def transform(self, X: pd.DataFrame) -> pd.DataFrame:
        """
        Transform data by imputing missing values.
        
        Parameters
        ----------
        X : pd.DataFrame
            Data to transform
            
        Returns
        -------
        pd.DataFrame
            Transformed data with imputed values
        """
        X = self._validate_input(X)
        X_imputed = X.copy()
        
        # Create missingness indicators if requested
        if self.create_missingness_indicators:
            for col in X.columns:
                if X[col].isnull().any():
                    X_imputed[f'{col}_was_missing'] = X[col].isnull().astype(int)
        
        # Apply imputation strategies
        for col in X.columns:
            if X[col].isnull().any():
                X_imputed[col] = self._impute_column(X[col], col)
        
        return X_imputed
    
    def _validate_input(self, X):
        """Validate and prepare input data."""
        if not isinstance(X, pd.DataFrame):
            raise ValueError("Input must be a pandas DataFrame")
        return X
    
    def _get_column_strategy(self, series: pd.Series) -> str:
        """Determine imputation strategy for a column."""
        col_name = series.name
        
        # Check for custom imputer
        if col_name in self.custom_imputers:
            return ImputationStrategy.CUSTOM
        
        # Use global strategy if specified
        if self.strategy != 'auto':
            return self.strategy
        
        # Auto-determine strategy based on data type
        if pd.api.types.is_numeric_dtype(series):
            return self.default_numeric_strategy
        else:
            return self.default_categorical_strategy
    
    def _impute_column(self, series: pd.Series, col_name: str) -> pd.Series:
        """Impute missing values in a single column."""
        strategy = self._get_column_strategy(series)
        
        if strategy == ImputationStrategy.CUSTOM:
            # Apply custom imputation function
            custom_func = self.custom_imputers[col_name]
            return custom_func(series)
        
        elif strategy == ImputationStrategy.MEDIAN:
            return series.fillna(self.statistics_[col_name])
        
        elif strategy == ImputationStrategy.MODE:
            if self.preserve_na_categories and series.dtype == 'object':
                return series.fillna('Missing')
            return series.fillna(self.statistics_[col_name])
        
        elif strategy == ImputationStrategy.MEAN:
            return series.fillna(self.statistics_[col_name])
        
        elif strategy == ImputationStrategy.FORWARD_FILL:
            return series.fillna(method='ffill').fillna(method='bfill')
        
        elif strategy == ImputationStrategy.BACKWARD_FILL:
            return series.fillna(method='bfill').fillna(method='ffill')
        
        elif strategy == ImputationStrategy.INTERPOLATE:
            if pd.api.types.is_numeric_dtype(series):
                return series.interpolate().fillna(method='bfill').fillna(method='ffill')
            else:
                return series.fillna(method='ffill').fillna(method='bfill')
        
        elif strategy == ImputationStrategy.KNN:
            if self.knn_imputer_ is not None and pd.api.types.is_numeric_dtype(series):
                # Apply KNN imputation (simplified for single column)
                return series.fillna(series.median())
            else:
                return series.fillna(series.median() if pd.api.types.is_numeric_dtype(series) else series.mode()[0])
        
        elif strategy == ImputationStrategy.MICE:
            if self.mice_imputer_ is not None and pd.api.types.is_numeric_dtype(series):
                # Apply MICE imputation (simplified for single column)
                return series.fillna(series.median())
            else:
                return series.fillna(series.median() if pd.api.types.is_numeric_dtype(series) else series.mode()[0])
        
        else:
            # Fallback to median/mode
            if pd.api.types.is_numeric_dtype(series):
                return series.fillna(series.median())
            else:
                mode_val = series.mode()
                return series.fillna(mode_val[0] if not mode_val.empty else 'Unknown')


def create_business_imputer(business_rules: Dict[str, Any]) -> Callable:
    """
    Create a business-logic-based imputer.
    
    Parameters
    ----------
    business_rules : dict
        Dictionary defining business rules for imputation
        
    Returns
    -------
    Callable
        Custom imputation function
        
    Examples
    --------
    >>> rules = {
    ...     'revenue': {'method': 'median_multiplier', 'factor': 0.8},
    ...     'category': {'method': 'fixed_value', 'value': 'unknown'}
    ... }
    >>> imputer_func = create_business_imputer(rules)
    """
    def business_imputer(series: pd.Series) -> pd.Series:
        col_name = series.name.lower()
        
        for pattern, rule in business_rules.items():
            if pattern in col_name:
                method = rule.get('method', 'median')
                
                if method == 'median_multiplier':
                    factor = rule.get('factor', 1.0)
                    fill_value = series.median() * factor
                    return series.fillna(fill_value)
                
                elif method == 'fixed_value':
                    value = rule.get('value', 'unknown')
                    return series.fillna(value)
                
                elif method == 'category_based':
                    # More complex business logic can be added here
                    pass
        
        # Default fallback
        if pd.api.types.is_numeric_dtype(series):
            return series.fillna(series.median())
        else:
            mode_val = series.mode()
            return series.fillna(mode_val[0] if not mode_val.empty else 'unknown')
    
    return business_imputer


def create_domain_specific_imputer(domain: str) -> Callable:
    """
    Create domain-specific imputation strategies.
    
    Parameters
    ----------
    domain : str
        Domain type ('financial', 'medical', 'iot', 'research')
        
    Returns
    -------
    Callable
        Domain-specific imputation function
    """
    def domain_imputer(series: pd.Series) -> pd.Series:
        col_name = series.name.lower()
        
        if domain == 'financial':
            if 'price' in col_name or 'value' in col_name:
                # Forward fill for financial prices
                return series.fillna(method='ffill').fillna(method='bfill')
            elif 'volume' in col_name:
                # Zero volume for missing trading data
                return series.fillna(0)
        
        elif domain == 'medical':
            if any(vital in col_name for vital in ['blood', 'heart', 'pressure', 'temp']):
                # Conservative median for vital signs
                return series.fillna(series.median())
            elif 'medication' in col_name or 'treatment' in col_name:
                # Explicit 'none' for missing medications
                return series.fillna('none')
        
        elif domain == 'iot':
            if 'sensor' in col_name or 'measurement' in col_name:
                # Interpolation for sensor data
                return series.interpolate().fillna(method='bfill')
            elif 'battery' in col_name:
                # Forward fill battery levels
                return series.fillna(method='ffill').fillna(100)
        
        elif domain == 'research':
            # Preserve missingness patterns for research
            if series.dtype == 'object':
                return series.fillna('Not Reported')
            else:
                return series.fillna(series.mean())  # Use mean for research
        
        # Default fallback
        if pd.api.types.is_numeric_dtype(series):
            return series.fillna(series.median())
        else:
            return series.fillna('unknown')
    
    return domain_imputer

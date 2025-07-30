"""Main Hygiea class that orchestrates all functionality."""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Union
from .core.standardizer import HygieaStandardizer


class Hygiea:
    """
    Main Hygiea class - Your data's superpower!
    
    A comprehensive toolkit for data cleaning, preprocessing, and analysis.
    Combines all Hygiea modules into a single, easy-to-use interface.
    """
    
    def __init__(self):
        """Initialize Hygiea with all component modules."""
        self.standardizer = HygieaStandardizer()
    
    def clean_data(
        self, 
        df: pd.DataFrame, 
        profile: str = 'default',
        custom_config: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        One-stop data cleaning function with predefined profiles.
        
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
        """
        df_clean = df.copy()
        
        if profile == 'default':
            # Standard cleaning pipeline
            df_clean = self.standardizer.standardize_columns(df_clean)
            df_clean = self._basic_type_conversion(df_clean)
            df_clean = self._simple_imputation(df_clean)
            
        elif profile == 'aggressive':
            # More thorough cleaning with advanced methods
            df_clean = self.standardizer.standardize_columns(df_clean)
            df_clean = self._basic_type_conversion(df_clean)
            df_clean = self._simple_imputation(df_clean)
            df_clean = self._handle_outliers(df_clean)
            
        elif profile == 'gentle':
            # Minimal cleaning with conservative settings
            df_clean = self.standardizer.standardize_columns(
                df_clean, remove_special=False, snake_case=False
            )
            df_clean = self._basic_type_conversion(df_clean)
            
        elif profile == 'minimal':
            # Only essential cleaning
            df_clean = self.standardizer.standardize_columns(df_clean, remove_special=False)
            
        elif profile == 'custom':
            # Use custom configuration
            if custom_config is None:
                raise ValueError("custom_config must be provided for 'custom' profile")
            
            config = custom_config
            
            if config.get('standardize_columns', True):
                df_clean = self.standardizer.standardize_columns(
                    df_clean, **config.get('standardize_params', {})
                )
            
            if config.get('convert_types', True):
                df_clean = self._basic_type_conversion(df_clean)
            
            if config.get('impute', True):
                df_clean = self._simple_imputation(df_clean)
            
            if config.get('handle_outliers', False):
                df_clean = self._handle_outliers(df_clean)
        
        else:
            raise ValueError(f"Unknown profile: {profile}")
        
        return df_clean
    
    def _basic_type_conversion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic data type conversion."""
        df = df.copy()
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Try to convert to numeric
                try:
                    # Check if it's mostly numeric
                    numeric_series = pd.to_numeric(df[col], errors='coerce')
                    if numeric_series.notna().sum() > len(df) * 0.7:  # 70% success rate
                        df[col] = numeric_series
                        continue
                except:
                    pass
                
                # Try to convert to boolean
                unique_vals = df[col].dropna().astype(str).str.lower().unique()
                bool_vals = {'true', 'false', 'yes', 'no', '1', '0', 't', 'f', 'y', 'n'}
                if len(unique_vals) <= 2 and all(val in bool_vals for val in unique_vals):
                    bool_map = {'true': True, 'false': False, 'yes': True, 'no': False,
                               '1': True, '0': False, 't': True, 'f': False,
                               'y': True, 'n': False}
                    df[col] = df[col].astype(str).str.lower().map(bool_map)
        
        return df
    
    def _simple_imputation(self, df: pd.DataFrame) -> pd.DataFrame:
        """Simple imputation for missing values."""
        df = df.copy()
        
        for col in df.columns:
            if df[col].isnull().any():
                if pd.api.types.is_numeric_dtype(df[col]):
                    # Use median for numeric columns
                    df[col].fillna(df[col].median(), inplace=True)
                else:
                    # Use mode for categorical columns
                    mode_val = df[col].mode()
                    if not mode_val.empty:
                        df[col].fillna(mode_val[0], inplace=True)
        
        return df
    
    def _handle_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Handle outliers using IQR method."""
        df = df.copy()
        
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            
            # Cap outliers
            df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def quick_profile(
        self, 
        df: pd.DataFrame,
        title: str = "Hygiea Data Profile",
        output_file: Optional[str] = None
    ) -> str:
        """Generate quick HTML profile report."""
        # Calculate basic statistics
        missing_count = df.isnull().sum().sum()
        missing_pct = (missing_count / (len(df) * len(df.columns))) * 100
        
        # Data quality score
        completeness = 1 - (missing_count / (len(df) * len(df.columns)))
        duplicates = df.duplicated().sum()
        uniqueness = 1 - (duplicates / len(df))
        quality_score = (completeness + uniqueness) / 2 * 100
        
        # Create HTML report
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{title}</title>
            <style>
                body {{ 
                    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                    margin: 0; 
                    padding: 20px; 
                    background-color: #f8f9fa; 
                }}
                .container {{ 
                    max-width: 1000px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px; 
                    border-radius: 10px; 
                    text-align: center; 
                    margin-bottom: 30px;
                }}
                .metrics {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                    gap: 20px; 
                    margin: 20px 0;
                }}
                .metric {{ 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 20px; 
                    border-radius: 8px; 
                    text-align: center;
                }}
                .metric-value {{ 
                    font-size: 2em; 
                    font-weight: bold; 
                    color: #495057;
                }}
                .metric-label {{ 
                    color: #6c757d; 
                    margin-top: 5px;
                }}
                .section {{ 
                    margin: 30px 0; 
                    padding: 20px; 
                    border: 1px solid #dee2e6; 
                    border-radius: 8px;
                }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 20px 0;
                }}
                th, td {{ 
                    border: 1px solid #dee2e6; 
                    padding: 12px; 
                    text-align: left;
                }}
                th {{ 
                    background: #f8f9fa; 
                    font-weight: 600;
                }}
                .quality-score {{ 
                    font-size: 3em; 
                    font-weight: bold; 
                    text-align: center; 
                    color: {'#28a745' if quality_score >= 80 else '#ffc107' if quality_score >= 60 else '#dc3545'};
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{title}</h1>
                    <p>Generated by Hygiea on {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h2>Dataset Overview</h2>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{len(df):,}</div>
                            <div class="metric-label">Rows</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{len(df.columns)}</div>
                            <div class="metric-label">Columns</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{df.memory_usage(deep=True).sum() / 1024**2:.1f} MB</div>
                            <div class="metric-label">Memory Usage</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{missing_count:,}</div>
                            <div class="metric-label">Missing Values</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Data Quality Score</h2>
                    <div class="quality-score">{quality_score:.1f}/100</div>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{completeness*100:.1f}%</div>
                            <div class="metric-label">Completeness</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{uniqueness*100:.1f}%</div>
                            <div class="metric-label">Uniqueness</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{duplicates}</div>
                            <div class="metric-label">Duplicates</div>
                        </div>
                    </div>
                </div>
                
                <div class="section">
                    <h2>Column Information</h2>
                    {self._generate_column_table(df)}
                </div>
                
            </div>
        </body>
        </html>
        """
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    def _generate_column_table(self, df: pd.DataFrame) -> str:
        """Generate HTML table for column information."""
        rows = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isnull().sum()
            missing_pct = (missing / len(df)) * 100
            unique = df[col].nunique()
            
            rows.append(f"""
            <tr>
                <td>{col}</td>
                <td>{dtype}</td>
                <td>{missing:,}</td>
                <td>{missing_pct:.1f}%</td>
                <td>{unique:,}</td>
            </tr>
            """)
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Column</th>
                    <th>Data Type</th>
                    <th>Missing Count</th>
                    <th>Missing %</th>
                    <th>Unique Values</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def __repr__(self) -> str:
        """String representation of Hygiea."""
        return """
    Hygiea - Your Data's Superpower!
    
    Available methods:
    • clean_data()           - One-stop data cleaning
    • quick_profile()        - HTML profile reports
    
    Ready to transform your messy data into gold!
        """

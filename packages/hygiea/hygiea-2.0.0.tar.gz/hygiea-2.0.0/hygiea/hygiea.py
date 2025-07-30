"""Enhanced main Hygiea class with custom imputation support."""

import pandas as pd
import numpy as np
from typing import Optional, Dict, Any, Union, Callable
from .core.standardizer import HygieaStandardizer
from .imputation.imputer import CustomImputer, ImputationStrategy


class Hygiea:
    """
    Enhanced Hygiea class - Your data's superpower with custom imputation!
    
    A comprehensive toolkit for data cleaning, preprocessing, and analysis
    with advanced missing value handling capabilities.
    """
    
    def __init__(self):
        """Initialize Hygiea with all component modules."""
        self.standardizer = HygieaStandardizer()
        self.imputer = CustomImputer()
    
    def clean_data(
        self, 
        df: pd.DataFrame, 
        profile: str = 'default',
        custom_config: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Enhanced one-stop data cleaning function with custom imputation support.
        
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
        """
        df_clean = df.copy()
        
        if profile == 'default':
            # Standard cleaning pipeline
            df_clean = self.standardizer.standardize_columns(df_clean)
            df_clean = self._basic_type_conversion(df_clean)
            df_clean = self._enhanced_imputation(df_clean, strategy='median')
            
        elif profile == 'aggressive':
            # More thorough cleaning with advanced methods
            df_clean = self.standardizer.standardize_columns(df_clean)
            df_clean = self._basic_type_conversion(df_clean)
            df_clean = self._enhanced_imputation(df_clean, strategy='knn')
            df_clean = self._handle_outliers(df_clean)
            df_clean = self._remove_duplicates(df_clean)
            
        elif profile == 'gentle':
            # Minimal cleaning with conservative settings
            df_clean = self.standardizer.standardize_columns(
                df_clean, remove_special=False, snake_case=False
            )
            df_clean = self._basic_type_conversion(df_clean)
            df_clean = self._enhanced_imputation(df_clean, strategy='mode')
            
        elif profile == 'minimal':
            # Only essential cleaning
            df_clean = self.standardizer.standardize_columns(df_clean, remove_special=False)
            
        elif profile == 'research':
            # Research-grade cleaning with missingness preservation
            df_clean = self.standardizer.standardize_columns(df_clean)
            df_clean = self._basic_type_conversion(df_clean)
            df_clean = self._enhanced_imputation(
                df_clean, 
                strategy='mean',  # Use mean for research
                preserve_na_categories=True,
                create_missingness_indicators=True
            )
            
        elif profile == 'financial':
            # Financial data specific cleaning
            df_clean = self.standardizer.standardize_columns(df_clean)
            df_clean = self._basic_type_conversion(df_clean)
            df_clean = self._enhanced_imputation(df_clean, strategy='ffill')  # Forward fill for prices
            df_clean = self._handle_financial_outliers(df_clean)
            
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
                impute_method = config.get('impute_method', 'median')
                custom_imputers = config.get('custom_imputers', {})
                
                df_clean = self._enhanced_imputation(
                    df_clean,
                    strategy=impute_method,
                    custom_imputers=custom_imputers,
                    knn_neighbors=config.get('knn_neighbors', 5),
                    mice_max_iter=config.get('mice_max_iter', 10),
                    preserve_na_categories=config.get('preserve_na_categories', False),
                    create_missingness_indicators=config.get('create_missingness_indicators', False)
                )
            
            if config.get('handle_outliers', False):
                df_clean = self._handle_outliers(df_clean, method=config.get('outlier_method', 'iqr'))
            
            if config.get('handle_duplicates', False):
                df_clean = self._remove_duplicates(df_clean)
        
        else:
            raise ValueError(f"Unknown profile: {profile}")
        
        return df_clean
    
    def _basic_type_conversion(self, df: pd.DataFrame) -> pd.DataFrame:
        """Enhanced data type conversion."""
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
                
                # Try to convert to datetime
                try:
                    if df[col].str.contains(r'\d{4}-\d{2}-\d{2}|\d{2}/\d{2}/\d{4}', 
                                          na=False).any():
                        df[col] = pd.to_datetime(df[col], errors='coerce')
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
    
    def _enhanced_imputation(
        self, 
        df: pd.DataFrame, 
        strategy: str = 'median',
        custom_imputers: Optional[Dict[str, Callable]] = None,
        **kwargs
    ) -> pd.DataFrame:
        """Enhanced imputation with custom function support."""
        
        # Create and configure imputer
        imputer = CustomImputer(
            strategy=strategy,
            custom_imputers=custom_imputers or {},
            **kwargs
        )
        
        # Fit and transform
        imputer.fit(df)
        return imputer.transform(df)
    
    def _handle_outliers(self, df: pd.DataFrame, method: str = 'iqr') -> pd.DataFrame:
        """Enhanced outlier handling with multiple methods."""
        df = df.copy()
        
        for col in df.select_dtypes(include=[np.number]).columns:
            if method == 'iqr':
                Q1 = df[col].quantile(0.25)
                Q3 = df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                # Cap outliers
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                
            elif method == 'zscore':
                mean = df[col].mean()
                std = df[col].std()
                threshold = 3
                
                # Cap outliers beyond 3 standard deviations
                lower_bound = mean - threshold * std
                upper_bound = mean + threshold * std
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
                
            elif method == 'clip':
                # Clip to 1st and 99th percentiles
                lower_bound = df[col].quantile(0.01)
                upper_bound = df[col].quantile(0.99)
                df[col] = df[col].clip(lower=lower_bound, upper=upper_bound)
        
        return df
    
    def _handle_financial_outliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """Special outlier handling for financial data."""
        df = df.copy()
        
        for col in df.select_dtypes(include=[np.number]).columns:
            col_lower = col.lower()
            
            if any(term in col_lower for term in ['price', 'value', 'amount']):
                # For prices/values, remove negative values and extreme highs
                df[col] = df[col].clip(lower=0, upper=df[col].quantile(0.99))
            
            elif 'volume' in col_lower:
                # For volumes, remove negatives
                df[col] = df[col].clip(lower=0)
            
            elif any(term in col_lower for term in ['return', 'change', 'pct']):
                # For returns/changes, cap at reasonable bounds
                df[col] = df[col].clip(lower=df[col].quantile(0.01), 
                                      upper=df[col].quantile(0.99))
        
        return df
    
    def _remove_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Remove duplicate rows."""
        return df.drop_duplicates().reset_index(drop=True)
    
    def quick_profile(
        self, 
        df: pd.DataFrame,
        title: str = "Hygiea Data Profile",
        output_file: Optional[str] = None
    ) -> str:
        """Generate enhanced HTML profile report."""
        # Calculate enhanced statistics
        missing_count = df.isnull().sum().sum()
        missing_pct = (missing_count / (len(df) * len(df.columns))) * 100
        
        # Data quality score components
        completeness = 1 - (missing_count / (len(df) * len(df.columns)))
        duplicates = df.duplicated().sum()
        uniqueness = 1 - (duplicates / len(df))
        
        # Consistency score
        consistency = self._calculate_consistency_score(df)
        
        # Overall quality score
        quality_score = (completeness * 0.4 + uniqueness * 0.3 + consistency * 0.3) * 100
        
        # Detect data issues
        issues = self._detect_data_issues(df)
        
        # Create enhanced HTML report
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
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    min-height: 100vh;
                }}
                .container {{ 
                    max-width: 1200px; 
                    margin: 0 auto; 
                    background: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                }}
                .header {{ 
                    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    color: white; 
                    padding: 30px; 
                    border-radius: 15px; 
                    text-align: center; 
                    margin-bottom: 30px;
                    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
                }}
                .header h1 {{ margin: 0; font-size: 2.5em; }}
                .header p {{ margin: 10px 0 0 0; opacity: 0.9; }}
                .metrics {{ 
                    display: grid; 
                    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); 
                    gap: 20px; 
                    margin: 20px 0;
                }}
                .metric {{ 
                    background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%); 
                    padding: 25px; 
                    border-radius: 10px; 
                    text-align: center;
                    box-shadow: 0 3px 10px rgba(0,0,0,0.1);
                    transition: transform 0.2s;
                }}
                .metric:hover {{ transform: translateY(-2px); }}
                .metric-value {{ 
                    font-size: 2.2em; 
                    font-weight: bold; 
                    color: #495057;
                    margin-bottom: 5px;
                }}
                .metric-label {{ 
                    color: #6c757d; 
                    font-weight: 500;
                }}
                .section {{ 
                    margin: 30px 0; 
                    padding: 25px; 
                    border: 1px solid #dee2e6; 
                    border-radius: 10px;
                    background: #f8f9fa;
                }}
                .section h2 {{ color: #495057; margin-top: 0; }}
                table {{ 
                    border-collapse: collapse; 
                    width: 100%; 
                    margin: 20px 0;
                    background: white;
                    border-radius: 8px;
                    overflow: hidden;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
                }}
                th, td {{ 
                    border: 1px solid #dee2e6; 
                    padding: 15px; 
                    text-align: left;
                }}
                th {{ 
                    background: linear-gradient(135deg, #495057 0%, #6c757d 100%); 
                    color: white;
                    font-weight: 600;
                }}
                .quality-score {{ 
                    font-size: 4em; 
                    font-weight: bold; 
                    text-align: center; 
                    color: {'#28a745' if quality_score >= 80 else '#ffc107' if quality_score >= 60 else '#dc3545'};
                    text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
                }}
                .issues-list {{ 
                    background: #fff3cd; 
                    border: 1px solid #ffeaa7; 
                    border-radius: 8px; 
                    padding: 15px; 
                    margin: 10px 0;
                }}
                .issues-list h4 {{ color: #856404; margin-top: 0; }}
                .issues-list ul {{ margin: 0; padding-left: 20px; }}
                .issues-list li {{ color: #856404; margin: 5px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🧹 {title}</h1>
                    <p>Enhanced Data Quality Report • Generated by Hygiea v2.0 • {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="section">
                    <h2>📊 Dataset Overview</h2>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{len(df):,}</div>
                            <div class="metric-label">Total Rows</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{len(df.columns)}</div>
                            <div class="metric-label">Total Columns</div>
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
                    <h2>🎯 Data Quality Assessment</h2>
                    <div class="quality-score">{quality_score:.1f}/100</div>
                    <div class="metrics">
                        <div class="metric">
                            <div class="metric-value">{completeness*100:.1f}%</div>
                            <div class="metric-label">Data Completeness</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{uniqueness*100:.1f}%</div>
                            <div class="metric-label">Data Uniqueness</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{consistency*100:.1f}%</div>
                            <div class="metric-label">Data Consistency</div>
                        </div>
                        <div class="metric">
                            <div class="metric-value">{duplicates}</div>
                            <div class="metric-label">Duplicate Rows</div>
                        </div>
                    </div>
                </div>
                
                {self._generate_issues_section(issues)}
                
                <div class="section">
                    <h2>📋 Column Information</h2>
                    {self._generate_enhanced_column_table(df)}
                </div>
                
                <div class="section">
                    <h2>💡 Recommended Actions</h2>
                    {self._generate_recommendations(df, quality_score)}
                </div>
                
            </div>
        </body>
        </html>
        """
        
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
        
        return html_content
    
    def _calculate_consistency_score(self, df: pd.DataFrame) -> float:
        """Calculate data consistency score."""
        consistency = 1.0
        
        for col in df.columns:
            if df[col].dtype == 'object':
                # Check for mixed types (numbers stored as strings)
                try:
                    numeric_conversion = pd.to_numeric(df[col].dropna(), errors='coerce')
                    if numeric_conversion.notna().sum() > 0.5 * len(df[col].dropna()):
                        consistency -= 0.1
                except:
                    pass
                
                # Check for inconsistent formatting
                if len(df[col].dropna()) > 0:
                    unique_formats = df[col].dropna().astype(str).str.len().nunique()
                    if unique_formats > len(df[col].dropna()) * 0.3:
                        consistency -= 0.05
        
        return max(0, consistency)
    
    def _detect_data_issues(self, df: pd.DataFrame) -> Dict[str, list]:
        """Detect common data quality issues."""
        issues = {
            'high_missing': [],
            'potential_outliers': [],
            'mixed_types': [],
            'inconsistent_formatting': [],
            'duplicates': [],
            'suspicious_values': []
        }
        
        # High missing values
        for col in df.columns:
            missing_pct = (df[col].isnull().sum() / len(df)) * 100
            if missing_pct > 30:
                issues['high_missing'].append(f"{col}: {missing_pct:.1f}% missing")
        
        # Potential outliers
        for col in df.select_dtypes(include=[np.number]).columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.05:
                issues['potential_outliers'].append(f"{col}: {outliers} potential outliers")
        
        # Mixed types
        for col in df.columns:
            if df[col].dtype == 'object':
                try:
                    numeric_conversion = pd.to_numeric(df[col].dropna(), errors='coerce')
                    if 0.1 < numeric_conversion.notna().sum() / len(df[col].dropna()) < 0.9:
                        issues['mixed_types'].append(f"{col}: Mixed numeric/text data")
                except:
                    pass
        
        # Duplicates
        if df.duplicated().sum() > 0:
            issues['duplicates'].append(f"{df.duplicated().sum()} duplicate rows found")
        
        return issues
    
    def _generate_issues_section(self, issues: Dict[str, list]) -> str:
        """Generate HTML for issues section."""
        if not any(issues.values()):
            return """
            <div class="section">
                <h2>✅ Data Quality Issues</h2>
                <p style="color: #28a745; font-weight: bold; font-size: 1.2em;">
                    🎉 No major data quality issues detected! Your data looks great!
                </p>
            </div>
            """
        
        issues_html = """
        <div class="section">
            <h2>⚠️ Data Quality Issues</h2>
        """
        
        for issue_type, issue_list in issues.items():
            if issue_list:
                issue_title = issue_type.replace('_', ' ').title()
                issues_html += f"""
                <div class="issues-list">
                    <h4>🔍 {issue_title}</h4>
                    <ul>
                """
                for issue in issue_list:
                    issues_html += f"<li>{issue}</li>"
                
                issues_html += """
                    </ul>
                </div>
                """
        
        issues_html += "</div>"
        return issues_html
    
    def _generate_enhanced_column_table(self, df: pd.DataFrame) -> str:
        """Generate enhanced HTML table for column information."""
        rows = []
        for col in df.columns:
            dtype = str(df[col].dtype)
            missing = df[col].isnull().sum()
            missing_pct = (missing / len(df)) * 100
            unique = df[col].nunique()
            
            # Determine data quality status
            if missing_pct > 50:
                status = "🔴 High Missing"
                status_color = "#dc3545"
            elif missing_pct > 20:
                status = "🟡 Some Missing"
                status_color = "#ffc107"
            elif missing_pct > 0:
                status = "🟢 Low Missing"
                status_color = "#28a745"
            else:
                status = "✅ Complete"
                status_color = "#28a745"
            
            rows.append(f"""
            <tr>
                <td><strong>{col}</strong></td>
                <td>{dtype}</td>
                <td>{missing:,}</td>
                <td>{missing_pct:.1f}%</td>
                <td>{unique:,}</td>
                <td style="color: {status_color}; font-weight: bold;">{status}</td>
            </tr>
            """)
        
        return f"""
        <table>
            <thead>
                <tr>
                    <th>Column Name</th>
                    <th>Data Type</th>
                    <th>Missing Count</th>
                    <th>Missing %</th>
                    <th>Unique Values</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows)}
            </tbody>
        </table>
        """
    
    def _generate_recommendations(self, df: pd.DataFrame, quality_score: float) -> str:
        """Generate cleaning recommendations."""
        recommendations = []
        
        if quality_score < 60:
            recommendations.append("🚨 Consider using 'aggressive' cleaning profile for comprehensive data cleaning")
        elif quality_score < 80:
            recommendations.append("💡 Use 'default' cleaning profile for balanced data improvement")
        else:
            recommendations.append("✨ Data quality is good! 'gentle' cleaning profile should suffice")
        
        # Missing value recommendations
        missing_pct = (df.isnull().sum().sum() / (len(df) * len(df.columns))) * 100
        if missing_pct > 30:
            recommendations.append("💧 High missing data detected - consider KNN or MICE imputation")
        elif missing_pct > 10:
            recommendations.append("🔄 Moderate missing data - median/mode imputation recommended")
        
        # Outlier recommendations
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_cols = 0
        for col in numeric_cols:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            outliers = ((df[col] < (Q1 - 1.5 * IQR)) | (df[col] > (Q3 + 1.5 * IQR))).sum()
            if outliers > len(df) * 0.05:
                outlier_cols += 1
        
        if outlier_cols > 0:
            recommendations.append(f"📊 {outlier_cols} columns have significant outliers - consider outlier handling")
        
        # Duplicate recommendations
        duplicates = df.duplicated().sum()
        if duplicates > 0:
            recommendations.append(f"🔄 {duplicates} duplicate rows found - recommend removal")
        
        # CLI command recommendations
        if quality_score < 60:
            cmd = "hygiea clean your_data.csv --profile aggressive --handle-outliers --output cleaned_data.csv"
        else:
            cmd = "hygiea clean your_data.csv --profile default --output cleaned_data.csv"
        
        recommendations.append(f"💻 Suggested CLI command: <code>{cmd}</code>")
        
        rec_html = "<ul>"
        for rec in recommendations:
            rec_html += f"<li style='margin: 10px 0; font-size: 1.1em;'>{rec}</li>"
        rec_html += "</ul>"
        
        return rec_html
    
    def __repr__(self) -> str:
        """String representation of enhanced Hygiea."""
        return """
    🧹 Hygiea v2.0 - Your Data's Superpower!
    
    Enhanced features:
    • clean_data()                    - One-stop data cleaning with custom imputation
    • quick_profile()                 - Beautiful HTML reports with quality scores
    • Custom imputation support      - Bring your own missing value strategies
    • Multiple cleaning profiles     - From gentle to aggressive cleaning
    • CLI interface                  - Complete command-line toolkit
    • Research & financial profiles - Domain-specific cleaning strategies
    
    New in v2.0:
    ✨ Advanced missing value handling (KNN, MICE, custom functions)
    ✨ Data quality scoring and issue detection
    ✨ Enhanced HTML reports with recommendations
    ✨ Complete CLI interface with batch processing
    ✨ Domain-specific cleaning profiles
    
    Ready to transform your messy data into gold! 🚀
        """

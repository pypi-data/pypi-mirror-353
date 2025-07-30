"""Column name standardization utilities."""

import re
import pandas as pd
from typing import Dict, List, Optional


class HygieaStandardizer:
    """Handle column name standardization and cleaning."""
    
    @staticmethod
    def standardize_columns(
        df: pd.DataFrame, 
        lowercase: bool = True,
        remove_spaces: bool = True,
        remove_special: bool = True,
        snake_case: bool = True,
        custom_mappings: Optional[Dict[str, str]] = None
    ) -> pd.DataFrame:
        """
        Standardize column names according to specified rules.
        
        Parameters
        ----------
        df : pd.DataFrame
            Input dataframe
        lowercase : bool, default=True
            Convert to lowercase
        remove_spaces : bool, default=True
            Remove spaces
        remove_special : bool, default=True
            Remove special characters
        snake_case : bool, default=True
            Convert to snake_case
        custom_mappings : dict, optional
            Custom column name mappings
            
        Returns
        -------
        pd.DataFrame
            DataFrame with standardized column names
            
        Examples
        --------
        >>> df = pd.DataFrame({'User ID': [1, 2], 'First Name': ['A', 'B']})
        >>> standardizer = HygieaStandardizer()
        >>> clean_df = standardizer.standardize_columns(df)
        >>> print(clean_df.columns.tolist())
        ['user_id', 'first_name']
        """
        df = df.copy()
        columns = df.columns.tolist()
        
        for i, col in enumerate(columns):
            new_col = str(col)
            
            # Apply custom mappings first
            if custom_mappings and col in custom_mappings:
                new_col = custom_mappings[col]
            else:
                if lowercase:
                    new_col = new_col.lower()
                
                if remove_special:
                    # Remove special characters but keep spaces and underscores for now
                    new_col = re.sub(r'[^\w\s]', '', new_col)
                
                if remove_spaces or snake_case:
                    # Replace spaces with underscores
                    new_col = re.sub(r'\s+', '_', new_col.strip())
                
                if snake_case:
                    # Convert camelCase to snake_case
                    new_col = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', new_col).lower()
                    # Clean up multiple underscores
                    new_col = re.sub(r'_+', '_', new_col).strip('_')
                    
                # Ensure column name is valid Python identifier
                if new_col and not new_col[0].isalpha() and new_col[0] != '_':
                    new_col = 'col_' + new_col
                
                # Handle empty column names
                if not new_col or new_col == '_':
                    new_col = f'column_{i}'
            
            columns[i] = new_col
        
        # Handle duplicate column names
        columns = HygieaStandardizer._handle_duplicates(columns)
        df.columns = columns
        
        return df
    
    @staticmethod
    def _handle_duplicates(columns: List[str]) -> List[str]:
        """Handle duplicate column names by adding suffixes."""
        seen = {}
        result = []
        
        for col in columns:
            if col in seen:
                seen[col] += 1
                result.append(f"{col}_{seen[col]}")
            else:
                seen[col] = 0
                result.append(col)
        
        return result
    
    @staticmethod
    def suggest_column_names(df: pd.DataFrame) -> Dict[str, str]:
        """Suggest standardized column names without applying them."""
        suggestions = {}
        standardizer = HygieaStandardizer()
        temp_df = standardizer.standardize_columns(df)
        
        for old, new in zip(df.columns, temp_df.columns):
            if old != new:
                suggestions[old] = new
        
        return suggestions
    
    @staticmethod
    def check_column_issues(df: pd.DataFrame) -> Dict[str, List[str]]:
        """Check for common column name issues."""
        issues = {
            'has_spaces': [],
            'has_special_chars': [],
            'not_snake_case': [],
            'starts_with_number': [],
            'duplicates': [],
            'empty_or_invalid': []
        }
        
        column_counts = {}
        
        for col in df.columns:
            col_str = str(col)
            
            # Count for duplicates
            if col_str in column_counts:
                column_counts[col_str] += 1
                if col_str not in issues['duplicates']:
                    issues['duplicates'].append(col_str)
            else:
                column_counts[col_str] = 1
            
            # Check for spaces
            if ' ' in col_str:
                issues['has_spaces'].append(col_str)
            
            # Check for special characters
            if re.search(r'[^\w\s]', col_str):
                issues['has_special_chars'].append(col_str)
            
            # Check if not snake_case
            if re.search(r'[A-Z]', col_str) or ' ' in col_str:
                issues['not_snake_case'].append(col_str)
            
            # Check if starts with number
            if col_str and col_str[0].isdigit():
                issues['starts_with_number'].append(col_str)
            
            # Check for empty or invalid names
            if not col_str or col_str.isspace() or col_str == '':
                issues['empty_or_invalid'].append(col_str)
        
        return issues

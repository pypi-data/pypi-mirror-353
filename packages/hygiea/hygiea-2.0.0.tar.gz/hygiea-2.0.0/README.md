# 🚀 Hygiea: Your Data's New Superpower 🧹

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CLI](https://img.shields.io/badge/CLI-Enabled-green.svg)](https://github.com/yourusername/hygiea)

Tired of wrestling with messy spreadsheets and endless cleaning scripts? **Hygiea** is a comprehensive Python toolkit that handles **EVERYTHING** for data cleaning, preprocessing, and analysis - now with powerful CLI tools and custom imputation methods!

## ✨ Why Hygiea?

Stop wasting hours on repetitive data cleaning tasks. Hygiea transforms raw, messy data into clean, model-ready insights in **minutes**, not hours.

### 🎯 Key Features

- **🆔 Standardize**: Auto-lowercase and clean column names
- **🔄 Convert**: Detect/convert dates, numeric strings, booleans  
- **💧 Advanced Imputation**: Median/mode, KNN, MICE, or **custom functions**
- **⚖️ Winsorize**: Cap outliers via IQR or z-score
- **🧩 Encode**: One-hot, target, or label encoding
- **📊 EDA**: Summary stats, missing-value report, correlation
- **🌐 Profiling**: Interactive HTML reports with one line
- **🔄 Pipeline-Ready**: Drop-in sklearn transformer
- **💻 CLI Interface**: Complete command-line toolkit
- **🎛️ Custom Imputation**: Bring your own missing value strategies

## 🚀 Quick Start

### Installation

```bash
pip install -e .
```

### Python API Usage

```python
import pandas as pd
import hygiea as hg

# Load your messy data
df = pd.DataFrame({
    'User ID': [1, 2, 3],
    'First Name': ['John', 'Jane', 'Bob'],
    'Annual Income ($)': [50000, None, 75000]
})

# Clean it in one line!
df_clean = hg.clean_data(df)
print(df_clean.columns.tolist())
# Output: ['user_id', 'first_name', 'annual_income']

# Generate beautiful HTML report
hg.profile_data(df, output_file='report.html')

# Get smart cleaning suggestions
suggestions = hg.suggest_cleaning_strategy(df)
print(f"Recommended: {suggestions['recommended_profile']}")
```

### CLI Usage

```bash
# Clean a CSV file
hygiea clean data.csv --output clean_data.csv --profile aggressive

# Generate profile report
hygiea profile data.csv --output report.html --title "My Data Report"

# Get cleaning suggestions
hygiea suggest data.csv

# Quick clean with auto-detection
hygiea quick-clean messy_data.csv --output cleaned.csv

# Custom imputation
hygiea clean data.csv --impute-method knn --knn-neighbors 5
```

## 🎯 5 Powerful Use Cases

### 1. 📊 **E-commerce Customer Data Cleanup**

**Scenario**: You have messy customer data from multiple sources with inconsistent formats, missing values, and duplicate entries.

```python
import hygiea as hg
import pandas as pd

# Messy e-commerce data
customer_data = pd.DataFrame({
    'Customer_ID': [1, 2, 3, 4, 5, 5],  # Duplicate
    'First Name': ['John', 'jane', 'BOB', None, 'Alice', 'Alice'],
    'Email Address': ['john@email.com', 'JANE@EMAIL.COM', 'bob@domain', '', 'alice@test.com', 'alice@test.com'],
    'Annual Revenue ($)': [1200.50, None, 'invalid', 2500, 0, 0],
    'Registration Date': ['2023-01-15', '01/02/2023', 'invalid', '2023-03-01', None, None],
    'Is Premium?': ['Yes', 'no', '1', 'True', '', '']
})

# Clean with custom imputation
def revenue_imputer(series):
    """Custom imputation based on customer segment"""
    median_revenue = series.median()
    return series.fillna(median_revenue * 0.8)  # Conservative estimate

# Apply comprehensive cleaning
df_clean = hg.clean_data(
    customer_data, 
    profile='custom',
    custom_config={
        'standardize_columns': True,
        'convert_types': True,
        'handle_duplicates': True,
        'impute': True,
        'custom_imputers': {'annual_revenue': revenue_imputer}
    }
)

# CLI equivalent:
# hygiea clean customer_data.csv --profile aggressive --handle-duplicates --output clean_customers.csv
```

**Result**: Clean, standardized customer data ready for CRM systems and analytics.

### 2. 🏥 **Healthcare Data Preprocessing for ML**

**Scenario**: Preparing patient data for machine learning models with strict quality requirements.

```python
import hygiea as hg
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier

# Medical data with sensitive missing values
patient_data = pd.read_csv('patient_records.csv')

# Custom imputation for medical data
def safe_medical_imputer(series, method='median'):
    """Safe imputation for medical values"""
    if series.name.lower() in ['blood_pressure', 'heart_rate']:
        # Use age-adjusted median for vital signs
        return series.fillna(series.median())
    elif series.name.lower() in ['medication', 'treatment']:
        # Use 'none' for missing medications
        return series.fillna('none')
    else:
        return series.fillna(series.median() if series.dtype.kind in 'biufc' else series.mode()[0])

# Create ML pipeline with custom imputation
pipeline = Pipeline([
    ('clean', hg.get_transformer(
        profile='custom',
        custom_config={
            'impute_method': 'custom',
            'custom_imputers': {'default': safe_medical_imputer}
        }
    )),
    ('model', RandomForestClassifier())
])

# Train model with cleaned data
pipeline.fit(X_train, y_train)

# CLI equivalent:
# hygiea clean patient_records.csv --impute-method custom --medical-safe --output ml_ready.csv
```

**Result**: ML-ready healthcare data with medically appropriate imputation strategies.

### 3. 📈 **Financial Trading Data Analysis**

**Scenario**: Processing high-frequency trading data with outliers and missing market values.

```python
import hygiea as hg

# Trading data with market anomalies
trading_data = pd.DataFrame({
    'Timestamp': pd.date_range('2023-01-01', periods=1000, freq='1min'),
    'Stock_Price': np.random.normal(100, 5, 1000),
    'Volume': np.random.exponential(1000, 1000),
    'Bid_Ask_Spread': np.random.normal(0.05, 0.01, 1000)
})

# Introduce realistic issues
trading_data.loc[100:110, 'Stock_Price'] = None  # Market halt
trading_data.loc[500, 'Stock_Price'] = 1000  # Flash crash anomaly
trading_data.loc[750:760, 'Volume'] = 0  # No trading volume

# Custom financial imputation
def financial_forward_fill(series):
    """Forward-fill with financial logic"""
    return series.fillna(method='ffill').fillna(method='bfill')

# Clean financial data
df_clean = hg.clean_data(
    trading_data,
    profile='custom',
    custom_config={
        'handle_outliers': True,
        'outlier_method': 'financial',  # Custom outlier detection
        'impute': True,
        'custom_imputers': {
            'stock_price': financial_forward_fill,
            'volume': lambda x: x.fillna(0)  # Missing volume = no trades
        }
    }
)

# Generate trading report
hg.profile_data(df_clean, output_file='trading_analysis.html', title='Trading Data Quality Report')

# CLI equivalent:
# hygiea clean trading_data.csv --profile financial --outlier-method winsorize --impute-method forward-fill
```

**Result**: Clean trading data suitable for quantitative analysis and algorithmic trading.

### 4. 🌍 **IoT Sensor Data Processing**

**Scenario**: Cleaning environmental sensor data with irregular measurements and sensor failures.

```python
import hygiea as hg

# IoT sensor data with various issues
sensor_data = pd.DataFrame({
    'sensor_id': ['temp_01', 'humid_02', 'pressure_03'] * 100,
    'timestamp': pd.date_range('2023-01-01', periods=300, freq='15min'),
    'temperature': np.random.normal(22, 5, 300),
    'humidity': np.random.normal(45, 10, 300),
    'battery_level': np.random.uniform(0, 100, 300)
})

# Simulate sensor failures and anomalies
sensor_data.loc[50:70, 'temperature'] = None  # Sensor offline
sensor_data.loc[150, 'humidity'] = 150  # Impossible humidity reading
sensor_data.loc[200:210, 'battery_level'] = 0  # Dead battery

# Custom IoT imputation strategies
def sensor_interpolate(series):
    """Interpolate missing sensor values"""
    return series.interpolate(method='time').fillna(method='bfill')

def battery_impute(series):
    """Estimate battery level based on time decay"""
    return series.fillna(method='ffill').fillna(100)

# Clean IoT data
df_clean = hg.clean_data(
    sensor_data,
    profile='custom',
    custom_config={
        'handle_outliers': True,
        'outlier_bounds': {'humidity': (0, 100)},  # Physical constraints
        'impute': True,
        'custom_imputers': {
            'temperature': sensor_interpolate,
            'humidity': sensor_interpolate,
            'battery_level': battery_impute
        }
    }
)

# CLI equivalent:
# hygiea clean sensor_data.csv --impute-method interpolate --outlier-method clip --physical-bounds
```

**Result**: Reliable IoT data ready for real-time monitoring and predictive maintenance.

### 5. 🎓 **Academic Research Data Preparation**

**Scenario**: Preparing survey data from multiple research studies for meta-analysis.

```python
import hygiea as hg

# Multi-study survey data
research_data = pd.DataFrame({
    'Study_ID': ['A', 'B', 'C'] * 200,
    'Participant_Age': np.random.normal(35, 12, 600),
    'Response_Score': np.random.normal(50, 15, 600),
    'Education_Level': np.random.choice(['High School', 'Bachelor', 'Master', 'PhD', ''], 600),
    'Country': np.random.choice(['USA', 'Canada', 'UK', 'Germany', '', 'N/A'], 600)
})

# Introduce research-specific missing patterns
research_data.loc[research_data['Study_ID'] == 'C', 'Education_Level'] = ''  # Study C didn't collect education
research_data.loc[np.random.choice(600, 50), 'Response_Score'] = None  # Random non-responses

# Research-appropriate imputation
def multiple_imputation(series, n_imputations=5):
    """Multiple imputation for research data"""
    if series.dtype.kind in 'biufc':  # Numeric
        return series.fillna(series.mean())  # Use mean for research
    else:
        return series.fillna('Not Reported')  # Explicit missing category

# Clean research data
df_clean = hg.clean_data(
    research_data,
    profile='custom',
    custom_config={
        'standardize_columns': True,
        'preserve_na_categories': True,  # Keep track of missingness patterns
        'impute': True,
        'custom_imputers': {'default': multiple_imputation},
        'create_missingness_indicators': True  # Add missing value flags
    }
)

# Generate research report
suggestions = hg.suggest_cleaning_strategy(research_data)
print("Research Data Quality Assessment:")
for point in suggestions['rationale']:
    print(f"- {point}")

# CLI equivalent:
# hygiea clean research_data.csv --profile research --preserve-na --missing-indicators --output cleaned_research.csv
```

**Result**: Research-grade data with appropriate handling of missing values and missingness indicators for statistical analysis.

## 💧 Advanced Missing Value Handling

### Built-in Imputation Methods

```python
# Choose from multiple strategies
df_clean = hg.clean_data(df, profile='custom', custom_config={
    'impute_method': 'knn',  # Options: 'median', 'mode', 'knn', 'mice', 'custom'
    'knn_neighbors': 5,
    'mice_iterations': 10
})
```

### Custom Imputation Functions

```python
# Define your own imputation logic
def business_logic_imputer(series):
    """Custom imputation based on business rules"""
    if series.name == 'revenue':
        # Estimate revenue based on company size category
        return series.fillna(series.median() * 0.8)
    elif series.name == 'category':
        # Use 'other' for missing categories
        return series.fillna('other')
    return series.fillna(series.median())

# Apply custom imputation
df_clean = hg.clean_data(df, profile='custom', custom_config={
    'custom_imputers': {
        'revenue': business_logic_imputer,
        'category': lambda x: x.fillna('unknown')
    }
})
```

## 💻 Complete CLI Interface

```bash
# Basic commands
hygiea clean data.csv                          # Clean with default profile
hygiea profile data.csv --output report.html  # Generate HTML report
hygiea suggest data.csv                        # Get cleaning recommendations

# Advanced cleaning options
hygiea clean data.csv \
    --profile aggressive \
    --impute-method knn \
    --knn-neighbors 5 \
    --handle-outliers \
    --outlier-method iqr \
    --output cleaned.csv

# Batch processing
hygiea batch-clean *.csv --output-dir cleaned/

# Pipeline integration
hygiea pipeline data.csv model_config.yaml --output predictions.csv

# Interactive mode
hygiea interactive data.csv  # Opens interactive cleaning session
```

### Advanced Pipeline Integration

```python
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import hygiea as hg

# Seamless sklearn integration with custom imputation
pipeline = Pipeline([
    ('clean', hg.get_transformer(
        profile='custom',
        custom_config={
            'impute_method': 'knn',
            'custom_imputers': {'income': business_logic_imputer}
        }
    )),
    ('model', RandomForestClassifier())
])

# Train with messy data - Hygiea handles the rest!
pipeline.fit(X_train, y_train)
predictions = pipeline.predict(X_test)
```

## 📊 Cleaning Profiles

Choose the right cleaning intensity for your data:

```python
# Gentle cleaning (minimal changes)
df_gentle = hg.clean_data(df, profile='gentle')

# Default cleaning (balanced approach)  
df_default = hg.clean_data(df, profile='default')

# Aggressive cleaning (thorough transformation)
df_aggressive = hg.clean_data(df, profile='aggressive')

# Research-grade cleaning (academic standards)
df_research = hg.clean_data(df, profile='research')

# Financial data cleaning (trading-specific)
df_financial = hg.clean_data(df, profile='financial')

# Custom cleaning (full control)
custom_config = {
    'standardize_columns': True,
    'convert_types': True,
    'impute': True,
    'impute_method': 'mice',
    'handle_outliers': True,
    'custom_imputers': {'revenue': business_logic_imputer}
}
df_custom = hg.clean_data(df, profile='custom', custom_config=custom_config)
```

## 🎛️ Modular Usage

Use individual components for specific tasks:

```python
from hygiea import HygieaStandardizer, CustomImputer

# Standardize column names
standardizer = HygieaStandardizer()
df = standardizer.standardize_columns(df)

# Custom imputation
imputer = CustomImputer(strategy='custom', custom_func=business_logic_imputer)
df_imputed = imputer.fit_transform(df)

# Get suggestions without applying
suggestions = standardizer.suggest_column_names(df)
print(suggestions)  # {'Old Name': 'new_name', ...}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_hygiea.py
```

Test CLI functionality:

```bash
hygiea test --run-all-tests
```

## 📄 License

MIT License - feel free to use in your projects!

## 🌟 Show Your Support

If Hygiea saves you time and frustration, please ⭐ star this repo!

---

**🚀 Stop wasting hours on data cleaning!**  
**Turn raw data into model-ready insights in minutes with Hygiea! 🧹✨**

### CLI Quick Reference

```bash
# Core commands
hygiea clean <file>           # Clean data
hygiea profile <file>         # Generate report  
hygiea suggest <file>         # Get recommendations
hygiea quick-clean <file>     # Auto-clean

# Advanced options
--profile <gentle|default|aggressive|research|financial|custom>
--impute-method <median|mode|knn|mice|custom>
--custom-imputer <function_name>
--handle-outliers
--outlier-method <iqr|zscore|clip>
--preserve-na
--missing-indicators
--output <filename>

# Examples
hygiea clean data.csv --profile research --preserve-na --output clean.csv
hygiea profile data.csv --title "Data Quality Report" --output report.html
hygiea batch-clean *.csv --output-dir ./cleaned/
```

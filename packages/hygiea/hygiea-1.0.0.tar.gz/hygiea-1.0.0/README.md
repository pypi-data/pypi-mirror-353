# 🚀 Hygiea: Your Data's New Superpower 🧹

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Tired of wrestling with messy spreadsheets and endless cleaning scripts? **Hygiea** is a comprehensive Python toolkit that handles **EVERYTHING** for data cleaning, preprocessing, and analysis.

## ✨ Why Hygiea?

Stop wasting hours on repetitive data cleaning tasks. Hygiea transforms raw, messy data into clean, model-ready insights in **minutes**, not hours.

### 🎯 Key Features

- **🆔 Standardize**: Auto-lowercase and clean column names
- **🔄 Convert**: Detect/convert dates, numeric strings, booleans  
- **💧 Impute**: Median/mode, KNN, or MICE imputation
- **⚖️ Winsorize**: Cap outliers via IQR or z-score
- **🧩 Encode**: One-hot, target, or label encoding
- **📊 EDA**: Summary stats, missing-value report, correlation
- **🌐 Profiling**: Interactive HTML reports with one line
- **🔄 Pipeline-Ready**: Drop-in sklearn transformer

## 🚀 Quick Start

### Installation

```bash
pip install -e .
```

### Basic Usage

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

### Advanced Pipeline Integration

```python
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
import hygiea as hg

# Seamless sklearn integration
pipeline = Pipeline([
    ('clean', hg.get_transformer()),
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

# Custom cleaning (full control)
custom_config = {
    'standardize_columns': True,
    'convert_types': True,
    'impute': True,
    'handle_outliers': True
}
df_custom = hg.clean_data(df, profile='custom', custom_config=custom_config)
```

## 🎛️ Modular Usage

Use individual components for specific tasks:

```python
from hygiea import HygieaStandardizer

# Standardize column names
standardizer = HygieaStandardizer()
df = standardizer.standardize_columns(df)

# Get suggestions without applying
suggestions = standardizer.suggest_column_names(df)
print(suggestions)  # {'Old Name': 'new_name', ...}
```

## 🧪 Testing

Run the comprehensive test suite:

```bash
python test_hygiea.py
```

## 📄 License

MIT License - feel free to use in your projects!

## 🌟 Show Your Support

If Hygiea saves you time and frustration, please ⭐ star this repo!

---

**🚀 Stop wasting hours on data cleaning!**  
**Turn raw data into model-ready insights in minutes with Hygiea! 🧹✨**

"""
Main CLI interface for Hygiea.
"""

import click
import pandas as pd
import sys
from pathlib import Path
from typing import Optional

from ..api import (
    clean_data, 
    profile_data, 
    suggest_cleaning_strategy, 
    quick_clean,
    analyze_data
)
from ..imputation.imputer import create_domain_specific_imputer, create_business_imputer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress
from rich import print as rprint

console = Console()


@click.group()
@click.version_option()
def main():
    """🧹 Hygiea: Your Data's New Superpower
    
    A comprehensive toolkit for data cleaning and preprocessing.
    
    Examples:
        hygiea clean data.csv --output clean_data.csv
        hygiea profile data.csv --output report.html
        hygiea suggest data.csv
    """
    pass


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path')
@click.option('--profile', '-p', 
              type=click.Choice(['gentle', 'default', 'aggressive', 'research', 'financial', 'custom']),
              default='default', help='Cleaning profile')
@click.option('--impute-method', 
              type=click.Choice(['median', 'mode', 'mean', 'knn', 'mice', 'ffill', 'bfill', 'interpolate', 'custom']),
              help='Imputation method')
@click.option('--knn-neighbors', type=int, default=5, help='Number of neighbors for KNN imputation')
@click.option('--mice-iterations', type=int, default=10, help='Maximum iterations for MICE')
@click.option('--handle-outliers', is_flag=True, help='Handle outliers')
@click.option('--outlier-method', type=click.Choice(['iqr', 'zscore', 'clip']), default='iqr')
@click.option('--preserve-na', is_flag=True, help='Preserve NA as category')
@click.option('--missing-indicators', is_flag=True, help='Create missingness indicators')
@click.option('--domain', type=click.Choice(['financial', 'medical', 'iot', 'research']), 
              help='Domain-specific cleaning')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def clean(input_file, output, profile, impute_method, knn_neighbors, mice_iterations,
          handle_outliers, outlier_method, preserve_na, missing_indicators, domain, verbose):
    """Clean data file with specified options."""
    
    if verbose:
        console.print(f"🧹 [bold green]Cleaning {input_file}[/bold green]")
    
    try:
        # Load data
        with Progress() as progress:
            task = progress.add_task("Loading data...", total=100)
            df = pd.read_csv(input_file)
            progress.update(task, completed=100)
        
        if verbose:
            console.print(f"📊 Loaded data: {df.shape[0]:,} rows, {df.shape[1]} columns")
        
        # Build configuration
        config = {}
        
        if profile == 'custom':
            config = {
                'standardize_columns': True,
                'convert_types': True,
                'impute': True,
                'handle_outliers': handle_outliers,
                'outlier_method': outlier_method,
                'preserve_na_categories': preserve_na,
                'create_missingness_indicators': missing_indicators
            }
            
            if impute_method:
                config['impute_method'] = impute_method
                config['knn_neighbors'] = knn_neighbors
                config['mice_max_iter'] = mice_iterations
            
            if domain:
                config['custom_imputers'] = {'default': create_domain_specific_imputer(domain)}
        
        # Clean data
        with Progress() as progress:
            task = progress.add_task("Cleaning data...", total=100)
            
            if profile == 'custom':
                df_clean = clean_data(df, profile='custom', custom_config=config)
            else:
                df_clean = clean_data(df, profile=profile)
            
            progress.update(task, completed=100)
        
        # Output results
        if output:
            df_clean.to_csv(output, index=False)
            console.print(f"✅ [bold green]Cleaned data saved to {output}[/bold green]")
        else:
            # Print to stdout
            df_clean.to_csv(sys.stdout, index=False)
        
        if verbose:
            # Show cleaning summary
            original_missing = df.isnull().sum().sum()
            cleaned_missing = df_clean.isnull().sum().sum()
            
            table = Table(title="Cleaning Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Before", style="red")
            table.add_column("After", style="green")
            
            table.add_row("Missing Values", f"{original_missing:,}", f"{cleaned_missing:,}")
            table.add_row("Columns", str(len(df.columns)), str(len(df_clean.columns)))
            table.add_row("Memory (MB)", f"{df.memory_usage(deep=True).sum()/1024**2:.1f}", 
                         f"{df_clean.memory_usage(deep=True).sum()/1024**2:.1f}")
            
            console.print(table)
    
    except Exception as e:
        console.print(f"❌ [bold red]Error cleaning data: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output HTML file path')
@click.option('--title', help='Report title')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def profile(input_file, output, title, verbose):
    """Generate data profile report."""
    
    if verbose:
        console.print(f"📊 [bold blue]Profiling {input_file}[/bold blue]")
    
    try:
        # Load data
        df = pd.read_csv(input_file)
        
        if verbose:
            console.print(f"📈 Loaded data: {df.shape[0]:,} rows, {df.shape[1]} columns")
        
        # Generate profile
        report_title = title or f"Data Profile: {Path(input_file).stem}"
        
        with Progress() as progress:
            task = progress.add_task("Generating profile...", total=100)
            html_content = profile_data(df, title=report_title, output_file=output)
            progress.update(task, completed=100)
        
        if output:
            console.print(f"✅ [bold green]Profile report saved to {output}[/bold green]")
        else:
            # Print summary to console
            analysis = analyze_data(df)
            
            table = Table(title="Data Profile Summary")
            table.add_column("Metric", style="cyan")
            table.add_column("Value", style="white")
            
            table.add_row("Shape", f"{analysis['shape'][0]:,} × {analysis['shape'][1]}")
            table.add_row("Missing Values", f"{analysis['missing_count']:,} ({analysis['missing_percentage']:.1f}%)")
            table.add_row("Duplicate Rows", f"{analysis['duplicate_rows']:,} ({analysis['duplicate_percentage']:.1f}%)")
            table.add_row("Quality Score", f"{analysis['quality_score']:.1f}/100")
            table.add_row("Memory Usage", f"{analysis['memory_usage_mb']:.1f} MB")
            
            console.print(table)
    
    except Exception as e:
        console.print(f"❌ [bold red]Error generating profile: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def suggest(input_file, verbose):
    """Get cleaning suggestions for data."""
    
    if verbose:
        console.print(f"🔍 [bold yellow]Analyzing {input_file}[/bold yellow]")
    
    try:
        # Load data
        df = pd.read_csv(input_file)
        
        # Get suggestions
        suggestions = suggest_cleaning_strategy(df)
        
        # Display recommendations
        console.print(f"\n🎯 [bold green]Recommended Profile: {suggestions['recommended_profile']}[/bold green]")
        
        console.print("\n📋 [bold cyan]Rationale:[/bold cyan]")
        for point in suggestions['rationale']:
            console.print(f"  • {point}")
        
        if suggestions['warnings']:
            console.print("\n⚠️ [bold yellow]Warnings:[/bold yellow]")
            for warning in suggestions['warnings']:
                console.print(f"  • {warning}")
        
        console.print("\n📈 [bold blue]Expected Impact:[/bold blue]")
        for metric, impact in suggestions['estimated_impact'].items():
            console.print(f"  • {metric.replace('_', ' ').title()}: {impact}")
        
        # Show CLI command
        console.print(f"\n💡 [bold green]Suggested CLI command:[/bold green]")
        cmd = f"hygiea clean {input_file} --profile {suggestions['recommended_profile']} --output cleaned_{Path(input_file).stem}.csv"
        console.print(f"  {cmd}")
    
    except Exception as e:
        console.print(f"❌ [bold red]Error analyzing data: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', help='Output file path')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def quick_clean(input_file, output, verbose):
    """Quick clean with auto-detected optimal settings."""
    
    if verbose:
        console.print(f"⚡ [bold magenta]Quick cleaning {input_file}[/bold magenta]")
    
    try:
        # Load data
        df = pd.read_csv(input_file)
        
        # Quick clean with auto-detection
        with Progress() as progress:
            task = progress.add_task("Auto-cleaning...", total=100)
            df_clean = quick_clean(df)
            progress.update(task, completed=100)
        
        # Output results
        if output:
            df_clean.to_csv(output, index=False)
            console.print(f"✅ [bold green]Quick cleaned data saved to {output}[/bold green]")
        else:
            output = f"quick_cleaned_{Path(input_file).stem}.csv"
            df_clean.to_csv(output, index=False)
            console.print(f"✅ [bold green]Quick cleaned data saved to {output}[/bold green]")
        
        if verbose:
            # Show summary
            original_issues = df.isnull().sum().sum() + df.duplicated().sum()
            cleaned_issues = df_clean.isnull().sum().sum() + df_clean.duplicated().sum()
            
            console.print(f"🎉 Reduced data issues from {original_issues:,} to {cleaned_issues:,}")
    
    except Exception as e:
        console.print(f"❌ [bold red]Error in quick clean: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.argument('pattern', default='*.csv')
@click.option('--output-dir', '-d', default='cleaned', help='Output directory')
@click.option('--profile', '-p', default='default', help='Cleaning profile')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def batch_clean(pattern, output_dir, profile, verbose):
    """Batch clean multiple files."""
    
    import glob
    
    files = glob.glob(pattern)
    
    if not files:
        console.print(f"❌ [bold red]No files found matching pattern: {pattern}[/bold red]")
        sys.exit(1)
    
    # Create output directory
    Path(output_dir).mkdir(exist_ok=True)
    
    console.print(f"🔄 [bold blue]Batch cleaning {len(files)} files...[/bold blue]")
    
    with Progress() as progress:
        main_task = progress.add_task("Overall progress", total=len(files))
        
        for file_path in files:
            try:
                # Load and clean data
                df = pd.read_csv(file_path)
                df_clean = clean_data(df, profile=profile)
                
                # Save cleaned data
                output_file = Path(output_dir) / f"cleaned_{Path(file_path).name}"
                df_clean.to_csv(output_file, index=False)
                
                if verbose:
                    console.print(f"  ✅ Cleaned {file_path} -> {output_file}")
                
                progress.advance(main_task)
                
            except Exception as e:
                console.print(f"  ❌ Failed to clean {file_path}: {e}")
                progress.advance(main_task)
    
    console.print(f"🎉 [bold green]Batch cleaning completed! Results in {output_dir}/[/bold green]")


@main.command()
@click.argument('input_file', type=click.Path(exists=True))
def interactive(input_file):
    """Interactive data cleaning session."""
    
    console.print(f"🔧 [bold purple]Interactive Cleaning Session: {input_file}[/bold purple]")
    
    try:
        # Load data
        df = pd.read_csv(input_file)
        console.print(f"📊 Loaded {df.shape[0]:,} rows, {df.shape[1]} columns")
        
        # Show initial analysis
        analysis = analyze_data(df)
        console.print(f"📈 Quality Score: {analysis['quality_score']:.1f}/100")
        
        while True:
            console.print("\n🎛️ [bold cyan]Available actions:[/bold cyan]")
            console.print("1. View data summary")
            console.print("2. Clean with profile")
            console.print("3. Custom imputation")
            console.print("4. Generate profile report")
            console.print("5. Save and exit")
            console.print("q. Quit without saving")
            
            choice = click.prompt("Select action", type=str)
            
            if choice == '1':
                # Show data summary
                table = Table(title="Data Summary")
                table.add_column("Column", style="cyan")
                table.add_column("Type", style="white")
                table.add_column("Missing", style="red")
                table.add_column("Unique", style="green")
                
                for col in df.columns[:10]:  # Show first 10 columns
                    table.add_row(
                        col,
                        str(df[col].dtype),
                        str(df[col].isnull().sum()),
                        str(df[col].nunique())
                    )
                
                console.print(table)
                if len(df.columns) > 10:
                    console.print(f"... and {len(df.columns) - 10} more columns")
            
            elif choice == '2':
                profile = click.prompt("Choose profile", 
                                     type=click.Choice(['gentle', 'default', 'aggressive', 'research', 'financial']))
                df = clean_data(df, profile=profile)
                console.print(f"✅ Applied {profile} cleaning profile")
            
            elif choice == '3':
                console.print("Custom imputation not implemented in interactive mode yet")
            
            elif choice == '4':
                output_file = click.prompt("Report filename", default="interactive_report.html")
                profile_data(df, output_file=output_file, title=f"Interactive Report: {input_file}")
                console.print(f"✅ Report saved to {output_file}")
            
            elif choice == '5':
                output_file = click.prompt("Output filename", default=f"cleaned_{Path(input_file).name}")
                df.to_csv(output_file, index=False)
                console.print(f"✅ Cleaned data saved to {output_file}")
                break
            
            elif choice.lower() == 'q':
                console.print("👋 Exiting without saving")
                break
            
            else:
                console.print("❌ Invalid choice, please try again")
    
    except Exception as e:
        console.print(f"❌ [bold red]Error in interactive session: {e}[/bold red]")
        sys.exit(1)


@main.command()
@click.option('--run-all-tests', is_flag=True, help='Run comprehensive test suite')
def test(run_all_tests):
    """Test Hygiea functionality."""
    
    if run_all_tests:
        console.print("🧪 [bold blue]Running comprehensive test suite...[/bold blue]")
        
        # Import and run the test suite
        import subprocess
        import sys
        
        try:
            result = subprocess.run([sys.executable, 'test_hygiea.py'], 
                                  capture_output=True, text=True)
            
            if result.returncode == 0:
                console.print("✅ [bold green]All tests passed![/bold green]")
                console.print(result.stdout)
            else:
                console.print("❌ [bold red]Some tests failed![/bold red]")
                console.print(result.stderr)
                sys.exit(1)
                
        except FileNotFoundError:
            console.print("❌ [bold red]Test file not found. Run from package root directory.[/bold red]")
            sys.exit(1)
    
    else:
        # Quick functionality test
        console.print("🔍 [bold blue]Testing basic functionality...[/bold blue]")
        
        try:
            import hygiea as hg
            
            # Create test data
            test_df = pd.DataFrame({
                'test_col': [1, 2, None, 4, 5],
                'Test Col 2': ['a', 'b', 'c', None, 'e']
            })
            
            # Test cleaning
            cleaned = hg.clean_data(test_df)
            console.print("✅ Data cleaning: OK")
            
            # Test profiling
            html = hg.profile_data(test_df, title="Test")
            console.print("✅ Data profiling: OK")
            
            # Test suggestions
            suggestions = hg.suggest_cleaning_strategy(test_df)
            console.print("✅ Cleaning suggestions: OK")
            
            console.print("🎉 [bold green]Basic functionality test passed![/bold green]")
            
        except Exception as e:
            console.print(f"❌ [bold red]Functionality test failed: {e}[/bold red]")
            sys.exit(1)


if __name__ == '__main__':
    main()

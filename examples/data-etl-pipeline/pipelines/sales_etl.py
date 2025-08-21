# FlowerPower ETL Pipeline - Sales Data Processing
# This example demonstrates a typical ETL workflow with data validation and transformation

import os
from pathlib import Path
from typing import Dict, List, Tuple
import pandas as pd
from hamilton.function_modifiers import config, parameterize
from loguru import logger

from flowerpower.cfg import Config

# Load pipeline configuration
PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="sales_etl"
).pipeline.h_params


# === DATA LOADING ===

def raw_data(input_file: str) -> pd.DataFrame:
    """Load raw sales data from CSV file."""
    file_path = Path(__file__).parents[1] / input_file
    logger.info(f"Loading data from {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} records from {input_file}")
    return df


# === DATA VALIDATION ===
#@parameterize(**PARAMS.validation_report)
def validation_report(
    raw_data: pd.DataFrame,
    min_price: int | float,
    max_price: int | float,
    required_columns: List[str]
) -> Dict:
    """Generate a comprehensive validation report for the raw data."""
    report = {
        "total_records": len(raw_data),
        "missing_columns": [],
        "data_quality_issues": [],
        "price_violations": 0,
        "missing_values": {},
        "is_valid": True
    }
    
    # Check for required columns
    missing_cols = [col for col in required_columns if col not in raw_data.columns]
    if missing_cols:
        report["missing_columns"] = missing_cols
        report["is_valid"] = False
        logger.warning(f"Missing required columns: {missing_cols}")
    
    # Check for missing values
    missing_counts = raw_data.isnull().sum()
    report["missing_values"] = missing_counts[missing_counts > 0].to_dict()
    
    # Validate price range (if price column exists)
    if "price" in raw_data.columns:
        price_violations = raw_data[
            (raw_data["price"] < min_price) | (raw_data["price"] > max_price)
        ]
        report["price_violations"] = len(price_violations)
        
        if len(price_violations) > 0:
            report["data_quality_issues"].append(
                f"{len(price_violations)} records with invalid prices"
            )
    
    # Check for duplicate records
    duplicates = raw_data.duplicated().sum()
    if duplicates > 0:
        report["data_quality_issues"].append(f"{duplicates} duplicate records found")
    
    if report["data_quality_issues"] or report["missing_columns"]:
        report["is_valid"] = False
    
    logger.info(f"Validation complete. Valid: {report['is_valid']}")
    return report


@config.when(enable_validation=True)
def clean_data__true(raw_data: pd.DataFrame, validation_report: Dict) -> pd.DataFrame:
    """Clean and prepare the data based on validation results."""
    if not validation_report["is_valid"]:
        logger.warning("Data validation failed, but proceeding with cleaning...")
    
    df = raw_data.copy()
    
    # Convert date column to datetime
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        logger.info("Converted date column to datetime")
    
    # Remove duplicates
    initial_count = len(df)
    df = df.drop_duplicates()
    removed_dupes = initial_count - len(df)
    if removed_dupes > 0:
        logger.info(f"Removed {removed_dupes} duplicate records")
    
    # Clean price data
    if "price" in df.columns:
        # Remove negative prices
        df = df[df["price"] >= 0]
        # Fill missing prices with median
        if df["price"].isnull().any():
            median_price = df["price"].median()
            df["price"] = df["price"].fillna(median_price)
            logger.info(f"Filled missing prices with median: {median_price}")
    
    # Calculate derived fields
    if "price" in df.columns and "quantity" in df.columns:
        df["total_sales"] = df["price"] * df["quantity"]
        logger.info("Calculated total_sales column")
    
    logger.info(f"Data cleaning complete. Final record count: {len(df)}")
    return df


@config.when(enable_validation=False)
def clean_data__false(raw_data: pd.DataFrame) -> pd.DataFrame:
    """Simple data cleaning without validation (when validation is disabled)."""
    df = raw_data.copy()
    
    # Basic cleaning operations
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    
    if "price" in df.columns and "quantity" in df.columns:
        df["total_sales"] = df["price"] * df["quantity"]
    
    logger.info(f"Basic data cleaning complete. Record count: {len(df)}")
    return df


# === DATA TRANSFORMATION & AGGREGATION ===
#@parameterize(**PARAMS.sales_summary)
def sales_summary(
    clean_data: pd.DataFrame,
    group_by: List[str],
    metrics: List[str]
) -> pd.DataFrame:
    """Generate sales summary aggregated by specified dimensions."""
    if not all(col in clean_data.columns for col in group_by):
        missing = [col for col in group_by if col not in clean_data.columns]
        raise ValueError(f"Grouping columns not found in data: {missing}")
    
    # Prepare aggregation functions
    agg_funcs = {}
    if "total_sales" in metrics and "total_sales" in clean_data.columns:
        agg_funcs["total_sales"] = "sum"
    if "avg_price" in metrics and "price" in clean_data.columns:
        agg_funcs["price"] = "mean"
    if "total_quantity" in metrics and "quantity" in clean_data.columns:
        agg_funcs["quantity"] = "sum"
    
    if not agg_funcs:
        logger.warning("No valid aggregation functions found")
        return pd.DataFrame()
    
    # Perform aggregation
    summary = clean_data.groupby(group_by).agg(agg_funcs).reset_index()
    
    # Rename columns to match requested metrics
    column_mapping = {
        "price": "avg_price",
        "quantity": "total_quantity"
    }
    summary = summary.rename(columns=column_mapping)
    
    # Sort by total sales if available
    if "total_sales" in summary.columns:
        summary = summary.sort_values("total_sales", ascending=False)
    
    logger.info(f"Generated sales summary with {len(summary)} groups")
    return summary


# === DATA OUTPUT ===


@config.when(save_intermediate=True)
def processed_file_path__true(output_dir: str) -> str:
    """Save processed data and return the file path."""
    output_path = Path(__file__).parents[1] / output_dir
    output_path.mkdir(exist_ok=True)
    
    return str(output_path / "sales_summary.csv")

@config.when(save_intermediate=False)
def processed_file_path__false(output_dir: str) -> str:
    """Return a placeholder path when saving is disabled."""
    logger.info("Skipping processed file path generation (save_intermediate=False)")
    return "Data saving skipped (save_intermediate=False)"

@config.when(save_intermediate=True)
def save_processed_data(sales_summary: pd.DataFrame, processed_file_path: str) -> str:
    """Save the processed sales summary to a CSV file."""
    if isinstance(processed_file_path, str) and processed_file_path.endswith(".csv"):
        sales_summary.to_csv(processed_file_path, index=False)
        logger.info(f"Saved processed data to {processed_file_path}")
        return processed_file_path
    else:
        logger.info("Skipping file save (save_intermediate=False)")
        return "File save skipped"
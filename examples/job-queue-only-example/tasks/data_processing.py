"""
Data Processing Tasks for Job Queue

This module contains standalone task functions that can be executed
via the job queue without requiring Hamilton pipelines. These tasks
demonstrate various processing patterns commonly used in background
job processing.
"""

import hashlib
import json
import logging
import random
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


def simple_calculation(x: int, y: int, operation: str = "add") -> Dict[str, Any]:
    """
    Perform a simple mathematical calculation.

    Args:
        x: First number
        y: Second number
        operation: Operation to perform (add, subtract, multiply, divide)

    Returns:
        Dictionary with calculation results
    """
    logger.info(f"Performing {operation} calculation: {x} {operation} {y}")

    start_time = datetime.now()

    if operation == "add":
        result = x + y
    elif operation == "subtract":
        result = x - y
    elif operation == "multiply":
        result = x * y
    elif operation == "divide":
        if y == 0:
            raise ValueError("Cannot divide by zero")
        result = x / y
    else:
        raise ValueError(f"Unknown operation: {operation}")

    end_time = datetime.now()

    return {
        "operation": operation,
        "operands": {"x": x, "y": y},
        "result": result,
        "calculated_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "duration_ms": (end_time - start_time).total_seconds() * 1000,
    }


def process_batch_data(
    data_list: List[Dict[str, Any]], batch_size: int = 10
) -> Dict[str, Any]:
    """
    Process a batch of data items with simulated work.

    Args:
        data_list: List of data items to process
        batch_size: Number of items to process per batch

    Returns:
        Dictionary with batch processing results
    """
    logger.info(
        f"Processing batch of {len(data_list)} items in batches of {batch_size}"
    )

    start_time = datetime.now()
    processed_items = []
    batch_results = []

    # Process in batches
    for i in range(0, len(data_list), batch_size):
        batch = data_list[i : i + batch_size]
        batch_start = datetime.now()

        # Simulate processing work
        batch_processed = []
        for item in batch:
            # Add some processing metadata
            processed_item = item.copy()
            processed_item["processed_at"] = datetime.now().isoformat()
            processed_item["batch_id"] = i // batch_size
            processed_item["item_hash"] = hashlib.md5(
                json.dumps(item, sort_keys=True).encode()
            ).hexdigest()

            # Simulate some work
            time.sleep(0.1)
            batch_processed.append(processed_item)

        batch_end = datetime.now()
        batch_duration = (batch_end - batch_start).total_seconds()

        batch_results.append({
            "batch_id": i // batch_size,
            "items_processed": len(batch_processed),
            "duration_seconds": batch_duration,
            "completed_at": batch_end.isoformat(),
        })

        processed_items.extend(batch_processed)
        logger.info(f"Completed batch {i // batch_size} in {batch_duration:.2f}s")

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    return {
        "total_items": len(data_list),
        "processed_items": len(processed_items),
        "batch_size": batch_size,
        "total_batches": len(batch_results),
        "batch_results": batch_results,
        "processed_data": processed_items,
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "total_duration_seconds": total_duration,
        "avg_items_per_second": len(processed_items) / total_duration
        if total_duration > 0
        else 0,
    }


def generate_report(data_source: str, report_type: str = "summary") -> Dict[str, Any]:
    """
    Generate a report based on data source and type.

    Args:
        data_source: Path to data source or identifier
        report_type: Type of report to generate (summary, detailed, analysis)

    Returns:
        Dictionary with report results
    """
    logger.info(f"Generating {report_type} report for data source: {data_source}")

    start_time = datetime.now()

    # Simulate report generation work
    time.sleep(2)  # Simulate processing time

    # Generate mock report data based on type
    if report_type == "summary":
        report_data = {
            "total_records": random.randint(1000, 10000),
            "categories": ["A", "B", "C"],
            "avg_value": round(random.uniform(10, 100), 2),
            "trends": "positive",
        }
    elif report_type == "detailed":
        report_data = {
            "total_records": random.randint(1000, 10000),
            "breakdown": {
                "category_a": random.randint(100, 1000),
                "category_b": random.randint(100, 1000),
                "category_c": random.randint(100, 1000),
            },
            "metrics": {
                "mean": round(random.uniform(50, 150), 2),
                "median": round(random.uniform(40, 140), 2),
                "std_dev": round(random.uniform(10, 30), 2),
            },
            "outliers": random.randint(5, 50),
        }
    elif report_type == "analysis":
        report_data = {
            "correlation_matrix": [[1.0, 0.7, 0.3], [0.7, 1.0, 0.4], [0.3, 0.4, 1.0]],
            "feature_importance": {
                "feature_1": 0.45,
                "feature_2": 0.32,
                "feature_3": 0.23,
            },
            "model_accuracy": round(random.uniform(0.8, 0.95), 3),
            "recommendations": [
                "Increase data collection for feature_1",
                "Consider removing feature_3",
                "Validate model with external dataset",
            ],
        }
    else:
        raise ValueError(f"Unknown report type: {report_type}")

    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()

    return {
        "report_type": report_type,
        "data_source": data_source,
        "report_data": report_data,
        "generated_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "generation_time_seconds": duration,
        "status": "completed",
    }


def send_notification(
    recipient: str, message: str, channel: str = "email"
) -> Dict[str, Any]:
    """
    Send a notification via specified channel.

    Args:
        recipient: Notification recipient
        message: Message content
        channel: Notification channel (email, sms, slack)

    Returns:
        Dictionary with notification results
    """
    logger.info(f"Sending {channel} notification to {recipient}")

    start_time = datetime.now()

    # Simulate notification sending
    time.sleep(1)  # Simulate network call

    # Simulate success/failure
    success = random.random() > 0.1  # 90% success rate

    end_time = datetime.now()

    result = {
        "recipient": recipient,
        "message": message,
        "channel": channel,
        "sent_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "success": success,
        "message_id": f"msg_{hashlib.md5(f'{recipient}{message}{start_time}'.encode()).hexdigest()[:8]}",
    }

    if success:
        logger.info(f"Notification sent successfully: {result['message_id']}")
    else:
        logger.error(f"Failed to send notification to {recipient}")
        result["error"] = "Network timeout or service unavailable"

    return result


def cleanup_old_files(directory: str, days_old: int = 7) -> Dict[str, Any]:
    """
    Clean up files older than specified days.

    Args:
        directory: Directory path to clean
        days_old: Delete files older than this many days

    Returns:
        Dictionary with cleanup results
    """
    logger.info(f"Cleaning up files in {directory} older than {days_old} days")

    start_time = datetime.now()
    cutoff_date = start_time - timedelta(days=days_old)

    # Simulate file cleanup work
    time.sleep(0.5)  # Simulate filesystem operations

    # Mock cleanup results
    files_found = random.randint(10, 100)
    files_deleted = random.randint(5, files_found)
    space_freed_mb = round(random.uniform(50, 500), 2)

    end_time = datetime.now()

    return {
        "directory": directory,
        "cutoff_date": cutoff_date.isoformat(),
        "files_found": files_found,
        "files_deleted": files_deleted,
        "files_kept": files_found - files_deleted,
        "space_freed_mb": space_freed_mb,
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
    }


def long_running_computation(
    iterations: int = 100, delay_ms: int = 100
) -> Dict[str, Any]:
    """
    Perform a long-running computation task.

    Args:
        iterations: Number of computation iterations
        delay_ms: Delay between iterations in milliseconds

    Returns:
        Dictionary with computation results
    """
    logger.info(f"Starting long-running computation: {iterations} iterations")

    start_time = datetime.now()
    results = []

    for i in range(iterations):
        # Simulate computation work
        computation_result = {
            "iteration": i,
            "value": random.random() * 100,
            "timestamp": datetime.now().isoformat(),
        }
        results.append(computation_result)

        # Add delay to simulate work
        time.sleep(delay_ms / 1000)

        # Log progress every 25%
        if i > 0 and i % (iterations // 4) == 0:
            progress = (i / iterations) * 100
            logger.info(f"Computation progress: {progress:.1f}% ({i}/{iterations})")

    end_time = datetime.now()
    total_duration = (end_time - start_time).total_seconds()

    # Calculate statistics
    values = [r["value"] for r in results]
    avg_value = sum(values) / len(values)
    min_value = min(values)
    max_value = max(values)

    return {
        "iterations_completed": iterations,
        "total_duration_seconds": total_duration,
        "avg_iteration_time_ms": (total_duration * 1000) / iterations,
        "results_summary": {
            "average_value": round(avg_value, 3),
            "min_value": round(min_value, 3),
            "max_value": round(max_value, 3),
            "total_data_points": len(results),
        },
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "status": "completed",
        "detailed_results": results[-10:],  # Include last 10 results as sample
    }


def data_validation_task(
    data: List[Dict[str, Any]], validation_rules: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Validate data against specified rules.

    Args:
        data: List of data items to validate
        validation_rules: Dictionary of validation rules

    Returns:
        Dictionary with validation results
    """
    logger.info(
        f"Validating {len(data)} data items against {len(validation_rules)} rules"
    )

    start_time = datetime.now()

    valid_items = []
    invalid_items = []
    validation_errors = []

    for i, item in enumerate(data):
        item_valid = True
        item_errors = []

        # Apply validation rules
        for field, rules in validation_rules.items():
            if field not in item:
                if rules.get("required", False):
                    item_valid = False
                    item_errors.append(f"Missing required field: {field}")
                continue

            value = item[field]

            # Type validation
            if "type" in rules:
                expected_type = rules["type"]
                if expected_type == "int" and not isinstance(value, int):
                    item_valid = False
                    item_errors.append(
                        f"Field {field} must be integer, got {type(value).__name__}"
                    )
                elif expected_type == "str" and not isinstance(value, str):
                    item_valid = False
                    item_errors.append(
                        f"Field {field} must be string, got {type(value).__name__}"
                    )

            # Range validation for numbers
            if isinstance(value, (int, float)):
                if "min" in rules and value < rules["min"]:
                    item_valid = False
                    item_errors.append(
                        f"Field {field} value {value} below minimum {rules['min']}"
                    )
                if "max" in rules and value > rules["max"]:
                    item_valid = False
                    item_errors.append(
                        f"Field {field} value {value} above maximum {rules['max']}"
                    )

            # Length validation for strings
            if isinstance(value, str):
                if "min_length" in rules and len(value) < rules["min_length"]:
                    item_valid = False
                    item_errors.append(
                        f"Field {field} too short: {len(value)} < {rules['min_length']}"
                    )
                if "max_length" in rules and len(value) > rules["max_length"]:
                    item_valid = False
                    item_errors.append(
                        f"Field {field} too long: {len(value)} > {rules['max_length']}"
                    )

        if item_valid:
            valid_items.append(item)
        else:
            invalid_items.append({
                "item_index": i,
                "item_data": item,
                "errors": item_errors,
            })
            validation_errors.extend(item_errors)

        # Simulate processing time
        time.sleep(0.01)

    end_time = datetime.now()

    return {
        "total_items": len(data),
        "valid_items": len(valid_items),
        "invalid_items": len(invalid_items),
        "validation_success_rate": len(valid_items) / len(data) if data else 0,
        "validation_rules_applied": len(validation_rules),
        "invalid_item_details": invalid_items,
        "error_summary": list(set(validation_errors)),
        "started_at": start_time.isoformat(),
        "completed_at": end_time.isoformat(),
        "duration_seconds": (end_time - start_time).total_seconds(),
    }

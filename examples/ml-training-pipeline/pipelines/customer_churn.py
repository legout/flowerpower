# FlowerPower ML Pipeline - Customer Churn Prediction
# This example demonstrates a complete machine learning workflow with training, evaluation, and model persistence

import os
import joblib
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score
from hamilton.function_modifiers import config, parameterize
from loguru import logger

from flowerpower.cfg import Config

# Load pipeline configuration
PARAMS = Config.load(
    Path(__file__).parents[1], pipeline_name="customer_churn"
).pipeline.h_params


# === DATA LOADING ===

def raw_data(input_file: str) -> pd.DataFrame:
    """Load customer data from CSV file."""
    file_path = Path(__file__).parents[1] / input_file
    logger.info(f"Loading customer data from {file_path}")
    
    if not file_path.exists():
        raise FileNotFoundError(f"Input file not found: {file_path}")
    
    df = pd.read_csv(file_path)
    logger.info(f"Loaded {len(df)} customer records")
    return df


def train_test_data(raw_data: pd.DataFrame, target_column: str, test_size: float, random_state: int) -> Dict[str, pd.DataFrame]:
    """Split data into training and testing sets."""
    if target_column not in raw_data.columns:
        raise ValueError(f"Target column '{target_column}' not found in data")
    
    X = raw_data.drop(columns=[target_column])
    y = raw_data[target_column]
    
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )
    
    logger.info(f"Training set: {len(X_train)} samples")
    logger.info(f"Test set: {len(X_test)} samples")
    logger.info(f"Target distribution - Train: {y_train.value_counts().to_dict()}")
    
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": y_train,
        "y_test": y_test
    }


# === FEATURE ENGINEERING ===

def engineered_features(
    train_test_data: Dict[str, pd.DataFrame],
    categorical_columns: List[str],
    numerical_columns: List[str],
    scale_features: bool
) -> Dict[str, Any]:
    """Engineer features including encoding categorical variables and scaling numerical ones."""
    
    X_train = train_test_data["X_train"].copy()
    X_test = train_test_data["X_test"].copy()
    
    # Ensure all specified columns exist
    missing_cols = []
    for col in categorical_columns + numerical_columns:
        if col not in X_train.columns:
            missing_cols.append(col)
    
    if missing_cols:
        logger.warning(f"Missing columns: {missing_cols}")
        # Filter out missing columns
        categorical_columns = [col for col in categorical_columns if col in X_train.columns]
        numerical_columns = [col for col in numerical_columns if col in X_train.columns]
    
    # Store preprocessing objects
    preprocessors = {}
    
    # Encode categorical variables
    for col in categorical_columns:
        le = LabelEncoder()
        X_train[col] = le.fit_transform(X_train[col].astype(str))
        X_test[col] = le.transform(X_test[col].astype(str))
        preprocessors[f"{col}_encoder"] = le
        logger.info(f"Encoded categorical column: {col}")
    
    # Scale numerical features
    if scale_features and numerical_columns:
        scaler = StandardScaler()
        X_train[numerical_columns] = scaler.fit_transform(X_train[numerical_columns])
        X_test[numerical_columns] = scaler.transform(X_test[numerical_columns])
        preprocessors["scaler"] = scaler
        logger.info(f"Scaled numerical columns: {numerical_columns}")
    
    logger.info(f"Feature engineering complete. Final shape: {X_train.shape}")
    
    return {
        "X_train": X_train,
        "X_test": X_test,
        "y_train": train_test_data["y_train"],
        "y_test": train_test_data["y_test"],
        "preprocessors": preprocessors,
        "feature_names": X_train.columns.tolist()
    }


@config.when(enable_feature_selection=True)
def selected_features(engineered_features: Dict[str, Any]) -> Dict[str, Any]:
    """Perform feature selection using correlation analysis."""
    X_train = engineered_features["X_train"]
    y_train = engineered_features["y_train"]
    
    # Calculate feature importance using correlation with target
    correlations = []
    for col in X_train.columns:
        corr = abs(np.corrcoef(X_train[col], y_train)[0, 1])
        correlations.append((col, corr))
    
    # Sort by correlation and select top features
    correlations.sort(key=lambda x: x[1], reverse=True)
    selected_cols = [col for col, _ in correlations if not np.isnan(correlations[0][1])]
    
    # Keep at least 3 features, but not more than 80% of original features
    n_features = max(3, min(len(selected_cols), int(0.8 * len(X_train.columns))))
    selected_cols = selected_cols[:n_features]
    
    logger.info(f"Selected {len(selected_cols)} features: {selected_cols}")
    
    # Filter features
    result = engineered_features.copy()
    result["X_train"] = engineered_features["X_train"][selected_cols]
    result["X_test"] = engineered_features["X_test"][selected_cols]
    result["feature_names"] = selected_cols
    result["feature_correlations"] = dict(correlations)
    
    return result


@config.when(enable_feature_selection=False)
def selected_features(engineered_features: Dict[str, Any]) -> Dict[str, Any]:
    """Return all engineered features when feature selection is disabled."""
    logger.info("Feature selection disabled, using all engineered features")
    return engineered_features


# === MODEL TRAINING ===

def trained_model(
    selected_features: Dict[str, Any],
    algorithm: str,
    hyperparameters: Dict[str, Any]
) -> Dict[str, Any]:
    """Train the machine learning model based on specified algorithm and hyperparameters."""
    
    X_train = selected_features["X_train"]
    y_train = selected_features["y_train"]
    
    # Initialize model based on algorithm
    if algorithm == "random_forest":
        model = RandomForestClassifier(**hyperparameters)
    elif algorithm == "logistic_regression":
        model = LogisticRegression(**hyperparameters)
    elif algorithm == "gradient_boosting":
        model = GradientBoostingClassifier(**hyperparameters)
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")
    
    logger.info(f"Training {algorithm} model with parameters: {hyperparameters}")
    
    # Train the model
    model.fit(X_train, y_train)
    
    # Get feature importance (if available)
    feature_importance = {}
    if hasattr(model, 'feature_importances_'):
        feature_names = selected_features["feature_names"]
        importance_scores = model.feature_importances_
        feature_importance = dict(zip(feature_names, importance_scores))
        
        # Sort by importance
        feature_importance = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        logger.info(f"Top 3 important features: {list(feature_importance.keys())[:3]}")
    
    return {
        "model": model,
        "algorithm": algorithm,
        "hyperparameters": hyperparameters,
        "feature_importance": feature_importance,
        "training_samples": len(X_train),
        "n_features": X_train.shape[1]
    }


# === MODEL EVALUATION ===

@config.when(cross_validation=True)
def model_evaluation(
    trained_model: Dict[str, Any],
    selected_features: Dict[str, Any],
    cv_folds: int,
    scoring_metrics: List[str]
) -> Dict[str, Any]:
    """Evaluate the trained model using cross-validation and test set performance."""
    
    model = trained_model["model"]
    X_train = selected_features["X_train"]
    y_train = selected_features["y_train"]
    X_test = selected_features["X_test"]
    y_test = selected_features["y_test"]
    
    evaluation_results = {
        "algorithm": trained_model["algorithm"],
        "cross_validation": {},
        "test_performance": {},
        "model_info": {
            "training_samples": trained_model["training_samples"],
            "n_features": trained_model["n_features"]
        }
    }
    
    # Cross-validation
    logger.info(f"Performing {cv_folds}-fold cross-validation")
    for metric in scoring_metrics:
        if metric in ["accuracy", "precision", "recall", "f1", "roc_auc"]:
            cv_scores = cross_val_score(model, X_train, y_train, cv=cv_folds, scoring=metric)
            evaluation_results["cross_validation"][metric] = {
                "mean": cv_scores.mean(),
                "std": cv_scores.std(),
                "scores": cv_scores.tolist()
            }
            logger.info(f"CV {metric}: {cv_scores.mean():.4f} (+/- {cv_scores.std() * 2:.4f})")
    
    # Test set evaluation
    logger.info("Evaluating on test set")
    y_pred = model.predict(X_test)
    y_pred_proba = model.predict_proba(X_test)[:, 1] if hasattr(model, 'predict_proba') else None
    
    # Calculate test metrics
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    evaluation_results["test_performance"] = {
        "accuracy": accuracy_score(y_test, y_pred),
        "precision": precision_score(y_test, y_pred, average='weighted'),
        "recall": recall_score(y_test, y_pred, average='weighted'),
        "f1": f1_score(y_test, y_pred, average='weighted')
    }
    
    if y_pred_proba is not None:
        evaluation_results["test_performance"]["roc_auc"] = roc_auc_score(y_test, y_pred_proba)
    
    # Classification report
    evaluation_results["classification_report"] = classification_report(y_test, y_pred, output_dict=True)
    evaluation_results["confusion_matrix"] = confusion_matrix(y_test, y_pred).tolist()
    
    logger.info(f"Test accuracy: {evaluation_results['test_performance']['accuracy']:.4f}")
    
    return evaluation_results


@config.when(cross_validation=False)
def model_evaluation(
    trained_model: Dict[str, Any],
    selected_features: Dict[str, Any]
) -> Dict[str, Any]:
    """Simplified evaluation without cross-validation."""
    
    model = trained_model["model"]
    X_test = selected_features["X_test"]
    y_test = selected_features["y_test"]
    
    logger.info("Performing simple test set evaluation (CV disabled)")
    
    y_pred = model.predict(X_test)
    
    from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score
    
    evaluation_results = {
        "algorithm": trained_model["algorithm"],
        "test_performance": {
            "accuracy": accuracy_score(y_test, y_pred),
            "precision": precision_score(y_test, y_pred, average='weighted'),
            "recall": recall_score(y_test, y_pred, average='weighted'),
            "f1": f1_score(y_test, y_pred, average='weighted')
        },
        "model_info": {
            "training_samples": trained_model["training_samples"],
            "n_features": trained_model["n_features"]
        }
    }
    
    return evaluation_results


# === FEATURE IMPORTANCE ===

def feature_importance(trained_model: Dict[str, Any]) -> Dict[str, float]:
    """Extract and return feature importance from the trained model."""
    return trained_model.get("feature_importance", {})


# === MODEL PERSISTENCE ===

def model_artifacts(
    trained_model: Dict[str, Any],
    model_evaluation: Dict[str, Any],
    selected_features: Dict[str, Any],
    model_dir: str,
    save_model: bool,
    model_versioning: bool
) -> Dict[str, str]:
    """Save model artifacts including the trained model, preprocessors, and metadata."""
    
    if not save_model:
        return {"status": "Model saving disabled"}
    
    # Create model directory
    model_path = Path(__file__).parents[1] / model_dir
    model_path.mkdir(exist_ok=True)
    
    # Generate version suffix if versioning is enabled
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    version_suffix = f"_{timestamp}" if model_versioning else ""
    
    artifacts = {}
    
    # Save the trained model
    model_file = model_path / f"model{version_suffix}.joblib"
    joblib.dump(trained_model["model"], model_file)
    artifacts["model_file"] = str(model_file)
    logger.info(f"Saved model to {model_file}")
    
    # Save preprocessors
    if "preprocessors" in selected_features:
        preprocessor_file = model_path / f"preprocessors{version_suffix}.joblib"
        joblib.dump(selected_features["preprocessors"], preprocessor_file)
        artifacts["preprocessor_file"] = str(preprocessor_file)
        logger.info(f"Saved preprocessors to {preprocessor_file}")
    
    # Save model metadata
    metadata = {
        "timestamp": timestamp,
        "algorithm": trained_model["algorithm"],
        "hyperparameters": trained_model["hyperparameters"],
        "feature_names": selected_features["feature_names"],
        "evaluation_results": model_evaluation,
        "feature_importance": trained_model.get("feature_importance", {})
    }
    
    metadata_file = model_path / f"metadata{version_suffix}.json"
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2, default=str)
    artifacts["metadata_file"] = str(metadata_file)
    logger.info(f"Saved metadata to {metadata_file}")
    
    # Create a "latest" symlink if versioning is enabled
    if model_versioning:
        try:
            latest_model = model_path / "model_latest.joblib"
            latest_preprocessor = model_path / "preprocessors_latest.joblib"
            latest_metadata = model_path / "metadata_latest.json"
            
            # Remove existing symlinks
            for latest_file in [latest_model, latest_preprocessor, latest_metadata]:
                if latest_file.exists():
                    latest_file.unlink()
            
            # Create new symlinks
            latest_model.symlink_to(model_file.name)
            if "preprocessor_file" in artifacts:
                latest_preprocessor.symlink_to(Path(artifacts["preprocessor_file"]).name)
            latest_metadata.symlink_to(metadata_file.name)
            
            logger.info("Created 'latest' symlinks for easy access")
        except Exception as e:
            logger.warning(f"Could not create symlinks: {e}")
    
    return artifacts
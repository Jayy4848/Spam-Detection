"""
Professional ML Pipeline for SMS Classification
Includes data preprocessing, feature engineering, model training, and evaluation
"""

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.svm import LinearSVC
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    classification_report, confusion_matrix, roc_auc_score
)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import LabelEncoder
import logging
import joblib
from pathlib import Path
from typing import Dict, Tuple, Any
import re
import string

logger = logging.getLogger('ml_models')


class TextPreprocessor:
    """Advanced text preprocessing for SMS data"""
    
    def __init__(self):
        self.url_pattern = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        self.phone_pattern = re.compile(r'\b\d{10,}\b')
        self.email_pattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
        self.number_pattern = re.compile(r'\b\d+\b')
    
    def preprocess(self, text: str, preserve_case: bool = False) -> str:
        """
        Preprocess text with advanced cleaning
        
        Args:
            text: Input text
            preserve_case: Whether to preserve case (for some models)
        
        Returns:
            Preprocessed text
        """
        if not isinstance(text, str):
            return ""
        
        # Replace URLs with token
        text = self.url_pattern.sub(' URL_TOKEN ', text)
        
        # Replace phone numbers with token
        text = self.phone_pattern.sub(' PHONE_TOKEN ', text)
        
        # Replace emails with token
        text = self.email_pattern.sub(' EMAIL_TOKEN ', text)
        
        # Replace numbers with token
        text = self.number_pattern.sub(' NUM_TOKEN ', text)
        
        # Remove extra whitespace
        text = ' '.join(text.split())
        
        # Convert to lowercase if not preserving case
        if not preserve_case:
            text = text.lower()
        
        return text
    
    def extract_features(self, text: str) -> Dict[str, Any]:
        """Extract statistical features from text"""
        return {
            'length': len(text),
            'word_count': len(text.split()),
            'url_count': len(self.url_pattern.findall(text)),
            'phone_count': len(self.phone_pattern.findall(text)),
            'email_count': len(self.email_pattern.findall(text)),
            'number_count': len(self.number_pattern.findall(text)),
            'uppercase_ratio': sum(1 for c in text if c.isupper()) / len(text) if text else 0,
            'digit_ratio': sum(1 for c in text if c.isdigit()) / len(text) if text else 0,
            'special_char_ratio': sum(1 for c in text if c in string.punctuation) / len(text) if text else 0,
        }


class SMSClassificationPipeline:
    """
    Complete ML pipeline for SMS classification
    Supports multiple algorithms and ensemble methods
    """
    
    def __init__(self, models_dir: str):
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(parents=True, exist_ok=True)
        
        self.preprocessor = TextPreprocessor()
        self.label_encoder = LabelEncoder()
        
        # Model configurations
        self.models = {
            'naive_bayes': MultinomialNB(alpha=0.1),
            'logistic_regression': LogisticRegression(max_iter=1000, C=1.0),
            'random_forest': RandomForestClassifier(n_estimators=100, max_depth=20, random_state=42),
            'gradient_boosting': GradientBoostingClassifier(n_estimators=100, learning_rate=0.1, random_state=42),
            'svm': LinearSVC(C=1.0, max_iter=1000, random_state=42)
        }
        
        self.vectorizers = {
            'tfidf': TfidfVectorizer(
                max_features=5000,
                ngram_range=(1, 3),
                min_df=2,
                max_df=0.95,
                sublinear_tf=True
            ),
            'count': CountVectorizer(
                max_features=5000,
                ngram_range=(1, 2),
                min_df=2,
                max_df=0.95
            )
        }
        
        self.trained_pipelines = {}
        self.evaluation_results = {}
    
    def load_data(self, data_path: str) -> Tuple[pd.DataFrame, pd.Series]:
        """Load and prepare data"""
        logger.info(f"Loading data from {data_path}")
        
        df = pd.read_csv(data_path)
        
        # Handle different column names
        text_col = None
        label_col = None
        
        for col in df.columns:
            if col.lower() in ['text', 'message', 'sms']:
                text_col = col
            if col.lower() in ['label', 'category', 'class']:
                label_col = col
        
        if text_col is None or label_col is None:
            # Try to infer columns
            if len(df.columns) >= 2:
                text_col = df.columns[1] if len(df.columns[0]) < len(df.columns[1]) else df.columns[0]
                label_col = df.columns[0] if text_col == df.columns[1] else df.columns[1]
            else:
                raise ValueError("Could not identify text and label columns")
        
        logger.info(f"Using columns: text='{text_col}', label='{label_col}'")
        
        # Preprocess text
        df['text_clean'] = df[text_col].apply(self.preprocessor.preprocess)
        
        # Encode labels
        y = self.label_encoder.fit_transform(df[label_col])
        
        logger.info(f"Loaded {len(df)} samples with {len(self.label_encoder.classes_)} classes")
        logger.info(f"Classes: {self.label_encoder.classes_}")
        
        return df['text_clean'], y
    
    def train_model(
        self,
        X: pd.Series,
        y: np.ndarray,
        model_name: str = 'naive_bayes',
        vectorizer_name: str = 'tfidf',
        test_size: float = 0.2,
        cv_folds: int = 5
    ) -> Dict[str, Any]:
        """
        Train a single model with cross-validation
        
        Args:
            X: Text data
            y: Labels
            model_name: Name of the model to train
            vectorizer_name: Name of the vectorizer to use
            test_size: Test set size
            cv_folds: Number of cross-validation folds
        
        Returns:
            Dictionary with training results and metrics
        """
        logger.info(f"Training {model_name} with {vectorizer_name} vectorizer")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=test_size, random_state=42, stratify=y
        )
        
        # Create pipeline
        pipeline = Pipeline([
            ('vectorizer', self.vectorizers[vectorizer_name]),
            ('classifier', self.models[model_name])
        ])
        
        # Train
        pipeline.fit(X_train, y_train)
        
        # Predictions
        y_pred = pipeline.predict(X_test)
        y_pred_proba = None
        if hasattr(pipeline.named_steps['classifier'], 'predict_proba'):
            y_pred_proba = pipeline.predict_proba(X_test)
        
        # Evaluate
        metrics = self._compute_metrics(y_test, y_pred, y_pred_proba)
        
        # Cross-validation
        cv_scores = cross_val_score(
            pipeline, X_train, y_train,
            cv=StratifiedKFold(n_splits=cv_folds, shuffle=True, random_state=42),
            scoring='f1_weighted'
        )
        
        metrics['cv_scores'] = cv_scores.tolist()
        metrics['cv_mean'] = float(cv_scores.mean())
        metrics['cv_std'] = float(cv_scores.std())
        
        # Store pipeline
        pipeline_key = f"{model_name}_{vectorizer_name}"
        self.trained_pipelines[pipeline_key] = pipeline
        self.evaluation_results[pipeline_key] = metrics
        
        logger.info(f"Model {pipeline_key} trained successfully")
        logger.info(f"Test Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"Test F1 Score: {metrics['f1_weighted']:.4f}")
        logger.info(f"CV F1 Score: {metrics['cv_mean']:.4f} (+/- {metrics['cv_std']:.4f})")
        
        return metrics
    
    def _compute_metrics(
        self,
        y_true: np.ndarray,
        y_pred: np.ndarray,
        y_pred_proba: np.ndarray = None
    ) -> Dict[str, Any]:
        """Compute comprehensive evaluation metrics"""
        
        metrics = {
            'accuracy': float(accuracy_score(y_true, y_pred)),
            'precision_weighted': float(precision_score(y_true, y_pred, average='weighted', zero_division=0)),
            'recall_weighted': float(recall_score(y_true, y_pred, average='weighted', zero_division=0)),
            'f1_weighted': float(f1_score(y_true, y_pred, average='weighted', zero_division=0)),
            'precision_macro': float(precision_score(y_true, y_pred, average='macro', zero_division=0)),
            'recall_macro': float(recall_score(y_true, y_pred, average='macro', zero_division=0)),
            'f1_macro': float(f1_score(y_true, y_pred, average='macro', zero_division=0)),
        }
        
        # Per-class metrics
        report = classification_report(y_true, y_pred, output_dict=True, zero_division=0)
        metrics['classification_report'] = report
        
        # Confusion matrix
        cm = confusion_matrix(y_true, y_pred)
        metrics['confusion_matrix'] = cm.tolist()
        
        # ROC AUC if probabilities available
        if y_pred_proba is not None:
            try:
                metrics['roc_auc'] = float(roc_auc_score(
                    y_true, y_pred_proba, multi_class='ovr', average='weighted'
                ))
            except:
                pass
        
        return metrics
    
    def train_all_models(self, X: pd.Series, y: np.ndarray) -> Dict[str, Dict]:
        """Train all model combinations"""
        results = {}
        
        for model_name in self.models.keys():
            for vectorizer_name in self.vectorizers.keys():
                try:
                    metrics = self.train_model(X, y, model_name, vectorizer_name)
                    results[f"{model_name}_{vectorizer_name}"] = metrics
                except Exception as e:
                    logger.error(f"Error training {model_name}_{vectorizer_name}: {str(e)}")
        
        return results
    
    def save_best_model(self, metric: str = 'f1_weighted') -> str:
        """Save the best performing model"""
        if not self.evaluation_results:
            raise ValueError("No models trained yet")
        
        # Find best model
        best_model_key = max(
            self.evaluation_results.items(),
            key=lambda x: x[1][metric]
        )[0]
        
        best_pipeline = self.trained_pipelines[best_model_key]
        best_metrics = self.evaluation_results[best_model_key]
        
        # Save pipeline
        model_path = self.models_dir / 'best_model.pkl'
        joblib.dump(best_pipeline, model_path)
        
        # Save label encoder
        encoder_path = self.models_dir / 'label_encoder.pkl'
        joblib.dump(self.label_encoder, encoder_path)
        
        # Save metadata
        metadata = {
            'model_key': best_model_key,
            'metrics': best_metrics,
            'classes': self.label_encoder.classes_.tolist()
        }
        
        import json
        metadata_path = self.models_dir / 'model_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Best model saved: {best_model_key}")
        logger.info(f"Performance: {metric}={best_metrics[metric]:.4f}")
        
        return best_model_key
    
    def get_training_summary(self) -> pd.DataFrame:
        """Get summary of all trained models"""
        if not self.evaluation_results:
            return pd.DataFrame()
        
        summary_data = []
        for model_key, metrics in self.evaluation_results.items():
            summary_data.append({
                'model': model_key,
                'accuracy': metrics['accuracy'],
                'f1_weighted': metrics['f1_weighted'],
                'f1_macro': metrics['f1_macro'],
                'cv_mean': metrics['cv_mean'],
                'cv_std': metrics['cv_std']
            })
        
        df = pd.DataFrame(summary_data)
        df = df.sort_values('f1_weighted', ascending=False)
        
        return df

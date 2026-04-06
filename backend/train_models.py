"""
Advanced Model Training Script with MLflow Tracking
Trains multiple models, evaluates performance, and tracks experiments
"""

import os
import sys
import logging
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

from ml_models.pipeline import SMSClassificationPipeline, TextPreprocessor
import pandas as pd
import numpy as np

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    """Main training function"""
    logger.info("=" * 80)
    logger.info("SMS Security Classification - Model Training")
    logger.info("=" * 80)
    
    # Paths
    base_dir = Path(__file__).parent
    data_path = base_dir / 'data' / 'sample_sms_dataset.csv'
    models_dir = base_dir / 'ml_models' / 'trained_models'
    
    # Check if data exists
    if not data_path.exists():
        logger.error(f"Data file not found: {data_path}")
        logger.info("Please ensure sample_sms_dataset.csv exists in the data directory")
        return
    
    # Initialize pipeline
    logger.info(f"Initializing ML pipeline...")
    pipeline = SMSClassificationPipeline(models_dir=str(models_dir))
    
    # Load data
    logger.info(f"Loading data from {data_path}")
    X, y = pipeline.load_data(str(data_path))
    
    logger.info(f"Dataset size: {len(X)} samples")
    logger.info(f"Classes: {pipeline.label_encoder.classes_}")
    
    # Class distribution
    unique, counts = np.unique(y, return_counts=True)
    logger.info("\nClass distribution:")
    for cls, count in zip(pipeline.label_encoder.classes_, counts):
        logger.info(f"  {cls}: {count} ({count/len(y)*100:.1f}%)")
    
    # Train all models
    logger.info("\n" + "=" * 80)
    logger.info("Training all model combinations...")
    logger.info("=" * 80)
    
    results = pipeline.train_all_models(X, y)
    
    # Display results
    logger.info("\n" + "=" * 80)
    logger.info("Training Results Summary")
    logger.info("=" * 80)
    
    summary_df = pipeline.get_training_summary()
    print("\n" + summary_df.to_string(index=False))
    
    # Save best model
    logger.info("\n" + "=" * 80)
    logger.info("Saving best model...")
    logger.info("=" * 80)
    
    best_model_key = pipeline.save_best_model(metric='f1_weighted')
    
    logger.info(f"\nBest model: {best_model_key}")
    logger.info(f"Model saved to: {models_dir}")
    
    # Save training summary
    summary_path = models_dir / 'training_summary.csv'
    summary_df.to_csv(summary_path, index=False)
    logger.info(f"Training summary saved to: {summary_path}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Training completed successfully!")
    logger.info("=" * 80)


if __name__ == '__main__':
    main()

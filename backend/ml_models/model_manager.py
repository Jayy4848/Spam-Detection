"""
ML Model Manager - Handles model loading, caching, and versioning
"""

import os
import joblib
import logging
import hashlib
from pathlib import Path
from typing import Dict, Any, Optional
from django.core.cache import cache
from django.conf import settings

logger = logging.getLogger('ml_models')


class ModelManager:
    """
    Centralized model management system
    Handles model loading, caching, versioning, and lifecycle
    """
    
    _instance = None
    _models = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        
        self.models_dir = Path(settings.ML_MODELS_DIR)
        self.cache_timeout = getattr(settings, 'ML_CACHE_TIMEOUT', 3600)
        self.enable_caching = getattr(settings, 'ENABLE_CACHING', True)
        self._initialized = True
        
        logger.info("ModelManager initialized")
    
    def load_model(self, model_name: str, version: str = 'latest') -> Optional[Any]:
        """
        Load a model from disk with caching
        
        Args:
            model_name: Name of the model file
            version: Model version (default: 'latest')
        
        Returns:
            Loaded model object or None if not found
        """
        cache_key = f"model_{model_name}_{version}"
        
        # Try cache first
        if self.enable_caching:
            cached_model = cache.get(cache_key)
            if cached_model is not None:
                logger.debug(f"Model {model_name} loaded from cache")
                return cached_model
        
        # Load from disk
        model_path = self.models_dir / model_name
        
        if not model_path.exists():
            logger.error(f"Model file not found: {model_path}")
            return None
        
        try:
            model = joblib.load(model_path)
            logger.info(f"Model {model_name} loaded from disk")
            
            # Cache the model
            if self.enable_caching:
                cache.set(cache_key, model, timeout=self.cache_timeout)
            
            return model
        
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            return None
    
    def save_model(self, model: Any, model_name: str, metadata: Dict = None) -> bool:
        """
        Save a model to disk with metadata
        
        Args:
            model: Model object to save
            model_name: Name for the model file
            metadata: Optional metadata dictionary
        
        Returns:
            True if successful, False otherwise
        """
        try:
            model_path = self.models_dir / model_name
            self.models_dir.mkdir(parents=True, exist_ok=True)
            
            # Save model
            joblib.dump(model, model_path)
            logger.info(f"Model saved: {model_path}")
            
            # Save metadata if provided
            if metadata:
                metadata_path = model_path.with_suffix('.meta.json')
                import json
                with open(metadata_path, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            # Invalidate cache
            cache_key = f"model_{model_name}_latest"
            cache.delete(cache_key)
            
            return True
        
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {str(e)}")
            return False
    
    def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get information about a model"""
        model_path = self.models_dir / model_name
        
        if not model_path.exists():
            return {'exists': False}
        
        stat = model_path.stat()
        
        # Try to load metadata
        metadata_path = model_path.with_suffix('.meta.json')
        metadata = {}
        if metadata_path.exists():
            import json
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
        
        return {
            'exists': True,
            'size_bytes': stat.st_size,
            'modified_time': stat.st_mtime,
            'metadata': metadata
        }
    
    def list_models(self) -> list:
        """List all available models"""
        if not self.models_dir.exists():
            return []
        
        models = []
        for file_path in self.models_dir.glob('*.pkl'):
            info = self.get_model_info(file_path.name)
            models.append({
                'name': file_path.name,
                'info': info
            })
        
        return models
    
    def compute_model_hash(self, model_path: Path) -> str:
        """Compute hash of model file for versioning"""
        hasher = hashlib.sha256()
        with open(model_path, 'rb') as f:
            for chunk in iter(lambda: f.read(4096), b''):
                hasher.update(chunk)
        return hasher.hexdigest()[:16]


# Singleton instance
model_manager = ModelManager()

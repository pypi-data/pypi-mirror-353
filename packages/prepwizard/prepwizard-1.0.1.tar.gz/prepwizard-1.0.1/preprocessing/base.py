from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Generic, TypeVar, Tuple
from pathlib import Path
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import pickle
import joblib


# Generic type definitions for maximum flexibility
InputDataType = TypeVar('InputDataType')
OutputDataType = TypeVar('OutputDataType')
TargetType = TypeVar('TargetType')


class MLTask(str, Enum):
    """Types of ML tasks"""
    CLASSIFICATION = "classification"
    REGRESSION = "regression"
    CLUSTERING = "clustering"
    ANOMALY_DETECTION = "anomaly_detection"


class PreprocessingConfig(BaseModel):
    """Universal configuration for any ML preprocessing task"""
    model_config = ConfigDict(
        extra='allow',  # Allow project-specific fields
        validate_assignment=True
    )
    
    # Universal settings
    ml_task: MLTask
    test_size: float = Field(default=0.2, ge=0.0, le=1.0)
    random_state: Optional[int] = Field(default=42, ge=0)
    
    # Common flags (projects can override)
    handle_missing_values: bool = True
    remove_duplicates: bool = True
    scale_features: bool = True
    
    # Project-specific configs go in extra fields
    # Example: target_column, categorical_features, etc.


class PreprocessingMetadata(BaseModel):
    """Metadata tracking for any preprocessing operation"""
    model_config = ConfigDict(frozen=True)
    
    ml_task: MLTask
    input_shape: Tuple[int, ...]
    output_shape: Tuple[int, ...]
    feature_names: Optional[List[str]] = None
    target_name: Optional[str] = None
    preprocessing_steps: List[str] = Field(default_factory=list)
    data_quality_metrics: Dict[str, float] = Field(default_factory=dict)


class BaseMLPreprocessor(ABC, Generic[InputDataType, OutputDataType, TargetType]):
    """
    Abstract base preprocessor for ANY ML project.
    
    Inherit from this class for your specific ML project:
    
    Example:
        class TitanicPreprocessor(BaseMLPreprocessor[pd.DataFrame, np.ndarray, np.ndarray]):
            # Implement methods for Titanic-specific preprocessing
            
        class HousePricePreprocessor(BaseMLPreprocessor[pd.DataFrame, pd.DataFrame, pd.Series]):
            # Implement methods for house price-specific preprocessing
    """
    
    def __init__(self, config: PreprocessingConfig):
        self.config = config
        self.metadata: Optional[PreprocessingMetadata] = None
        self.is_fitted: bool = False
        self._fitted_params: Dict[str, Any] = {}
    
    # ============================================================================
    # CORE ABSTRACT METHODS - MUST BE IMPLEMENTED BY EVERY PROJECT
    # ============================================================================
    
    @abstractmethod
    def fit(self, X: InputDataType, y: Optional[TargetType] = None) -> 'BaseMLPreprocessor':
        """
        Learn preprocessing parameters from training data.
        
        Args:
            X: Input features (any format: DataFrame, array, images, text, etc.)
            y: Target variable (optional for unsupervised tasks)
            
        Returns:
            Self for method chaining
        """
        pass
    
    @abstractmethod
    def transform(self, X: InputDataType) -> OutputDataType:
        """
        Apply preprocessing transformations to data.
        
        Args:
            X: Input data to transform
            
        Returns:
            Transformed data ready for ML model
            
        Raises:
            ValueError: If preprocessor is not fitted
        """
        pass
    
    @abstractmethod
    def validate_input(self, X: InputDataType, y: Optional[TargetType] = None) -> bool:
        """
        Validate that input data is suitable for this preprocessor.
        
        Args:
            X: Input features
            y: Target variable (optional)
            
        Returns:
            True if valid, False otherwise
        """
        pass
    
    # ============================================================================
    # OPTIONAL METHODS - IMPLEMENT IF NEEDED FOR YOUR PROJECT
    # ============================================================================
    
    def fit_transform(self, X: InputDataType, y: Optional[TargetType] = None) -> OutputDataType:
        """
        Fit and transform in one step.
        Default implementation - override if you need custom behavior.
        """
        return self.fit(X, y).transform(X)
    
    def inverse_transform(self, X: OutputDataType) -> InputDataType:
        """
        Reverse the preprocessing (if possible).
        Override this if your preprocessing is reversible.
        """
        raise NotImplementedError("Inverse transform not implemented for this preprocessor")
    
    def get_feature_names(self) -> Optional[List[str]]:
        """
        Get names of features after preprocessing.
        Override this if your preprocessing changes feature names.
        """
        return None
    
    # ============================================================================
    # CONCRETE UTILITY METHODS - AVAILABLE TO ALL PROJECTS
    # ============================================================================
    
    def save(self, filepath: Union[str, Path]) -> None:
        """Save fitted preprocessor to disk"""
        if not self.is_fitted:
            raise ValueError("Cannot save unfitted preprocessor")
        
        save_data = {
            'config': self.config.model_dump(),
            'metadata': self.metadata.model_dump() if self.metadata else None,
            'fitted_params': self._fitted_params,
            'class_name': self.__class__.__name__
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
    
    @classmethod
    def load(cls, filepath: Union[str, Path]) -> 'BaseMLPreprocessor':
        """Load fitted preprocessor from disk"""
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)
        
        # Recreate the preprocessor
        instance = cls(PreprocessingConfig(**save_data['config']))
        instance._fitted_params = save_data['fitted_params']
        instance.is_fitted = True
        
        if save_data['metadata']:
            instance.metadata = PreprocessingMetadata(**save_data['metadata'])
        
        return instance
    
    def get_params(self) -> Dict[str, Any]:
        """Get fitted parameters"""
        return self._fitted_params.copy()
    
    def set_params(self, **params) -> 'BaseMLPreprocessor':
        """Set fitted parameters (for advanced use cases)"""
        self._fitted_params.update(params)
        return self
    
    def reset(self) -> 'BaseMLPreprocessor':
        """Reset to unfitted state"""
        self.is_fitted = False
        self.metadata = None
        self._fitted_params.clear()
        return self
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(task={self.config.ml_task}, fitted={self.is_fitted})"

"""
Time-series Euclidean Space Interpolation (TESI)

This module implements the TESI algorithm for interpolating time series data
using various Euclidean space transformations.
"""

import numpy as np
import pandas as pd
from typing import Dict, Union, Callable


class TESI:
    """Time-series Euclidean Space Interpolation (TESI) class.
    
    This class implements various interpolation methods for time series data using
    Euclidean space transformations. The class handles zero values and near-zero
    values with special care to ensure numerical stability.
    
    Attributes:
        input_data (pd.DataFrame): Input data with m_samples and n_features.
        equation (str): The interpolation equation to use.
        start (float): The starting value for the interpolation sequence.
        augmentation_factor (int): Number of points to generate between each pair.
        
    Example:
        >>> import pandas as pd
        >>> from pydbox.tesi import TESI
        >>> df = pd.DataFrame({'A': [1, 2, 3], 'B': [4, 5, 6]})
        >>> interpolator = TESI(df, equation='Euc_p1', augmentation_factor=5)
        >>> result = interpolator.pd_frame()
    """
    
    # Define valid equation types
    VALID_EQUATIONS = {'Euc_p1', 'Euc_p2', 'Euc_p3', 'Euc_Log'}
    
    def __init__(
        self,
        input_data: pd.DataFrame,
        equation: str = 'Euc_p1',
        start: float = 0.01,
        augmentation_factor: int = 10,
        precision: int = 6,
        zero_threshold: float = 1e-10
    ) -> None:
        """Initialize the TESI interpolator.
        
        Args:
            input_data: DataFrame containing the time series data.
            equation: Interpolation equation to use.
            start: Starting value for the interpolation sequence (0 < start < 1).
            augmentation_factor: Number of points to generate between each pair.
            precision: Number of decimal places for floating point calculations.
            zero_threshold: Values below this threshold are treated as zero.
            
        Raises:
            TypeError: If input_data is not a pandas DataFrame.
            ValueError: If parameters are invalid.
        """
        self._validate_inputs(input_data, equation, start, augmentation_factor, precision, zero_threshold)
        
        self._input = input_data
        self._X = input_data.T.values
        self._start = start
        self._equation = equation
        self._augmentation_factor = augmentation_factor
        self._precision = precision
        self._zero_threshold = zero_threshold
        
        # Define interpolation equations with improved numerical stability
        self._equations: Dict[str, Callable] = {
            'Euc_p1': self._safe_linear,      # linear with zero handling
            'Euc_p2': self._safe_quadratic,   # quadratic with zero handling
            'Euc_p3': self._safe_cubic,       # cubic with zero handling
            'Euc_Log': self._safe_log         # logarithmic with zero handling
        }

    def _safe_linear(self, x: np.ndarray, x2: float) -> np.ndarray:
        """Safe linear interpolation handling zero values."""
        mask = abs(x2) < self._zero_threshold
        result = np.zeros_like(x)
        non_zero = ~mask
        if np.any(non_zero):
            result[non_zero] = np.round(x[non_zero]/x2, self._precision)
        return result

    def _safe_quadratic(self, x: np.ndarray, x2: float) -> np.ndarray:
        """Safe quadratic interpolation handling zero values."""
        mask = abs(x2) < self._zero_threshold
        result = np.zeros_like(x)
        non_zero = ~mask
        if np.any(non_zero):
            result[non_zero] = np.round(np.power(x[non_zero], 2)/np.power(x2, 2), self._precision)
        return result

    def _safe_cubic(self, x: np.ndarray, x2: float) -> np.ndarray:
        """Safe cubic interpolation handling zero values."""
        mask = abs(x2) < self._zero_threshold
        result = np.zeros_like(x)
        non_zero = ~mask
        if np.any(non_zero):
            result[non_zero] = np.round(np.power(x[non_zero], 3)/np.power(x2, 3), self._precision)
        return result

    def _safe_log(self, x: np.ndarray, x2: float) -> np.ndarray:
        """Safe logarithmic interpolation handling zero values."""
        mask = abs(x2) < self._zero_threshold
        result = np.zeros_like(x)
        non_zero = ~mask
        if np.any(non_zero):
            # Use log1p for better numerical stability with small values
            result[non_zero] = np.round(np.log1p(x[non_zero])/np.log1p(x2), self._precision)
        return result

    @staticmethod
    def _validate_inputs(
        input_data: pd.DataFrame,
        equation: str,
        start: float,
        augmentation_factor: int,
        precision: int,
        zero_threshold: float
    ) -> None:
        """Validate input parameters.
        
        Raises:
            TypeError: If input types are incorrect.
            ValueError: If parameter values are invalid.
        """
        if not isinstance(input_data, pd.DataFrame):
            raise TypeError("input_data must be a pandas DataFrame")
        if input_data.empty:
            raise ValueError("input_data cannot be empty")
            
        if not isinstance(equation, str):
            raise TypeError("equation must be a string")
        if equation not in TESI.VALID_EQUATIONS:
            raise ValueError(f"equation must be one of {TESI.VALID_EQUATIONS}")
            
        if not isinstance(start, (int, float)):
            raise TypeError("start must be a number")
        if not 0 < start < 1:
            raise ValueError("start must be between 0 and 1")
            
        if not isinstance(augmentation_factor, int):
            raise TypeError("augmentation_factor must be an integer")
        if augmentation_factor < 1:
            raise ValueError("augmentation_factor must be at least 1")
            
        if not isinstance(precision, int):
            raise TypeError("precision must be an integer")
        if precision < 1 or precision > 15:
            raise ValueError("precision must be between 1 and 15")

        if not isinstance(zero_threshold, float):
            raise TypeError("zero_threshold must be a float")
        if zero_threshold <= 0:
            raise ValueError("zero_threshold must be positive")

    def interpolate_vector(self, X: np.ndarray) -> np.ndarray:
        """Interpolate a single vector using the specified method.
        
        This method handles zero values by treating them as special cases:
        - If the vector is all zeros, returns a vector of zeros
        - If there are some zeros, interpolates only between non-zero values
        
        Args:
            X: Input vector to interpolate.
            
        Returns:
            np.ndarray: Interpolated vector with augmented points.
        """
        # Handle all-zero vector case
        if np.all(abs(X) < self._zero_threshold):
            return np.zeros(self._augmentation_factor * (len(X) - 1))

        # Calculate differences between consecutive points
        W = np.diff(X, axis=0).reshape(-1, 1)
        
        # Handle zero differences
        zero_diff_mask = abs(W) < self._zero_threshold
        W[zero_diff_mask] = self._zero_threshold  # Replace zeros with small value
        
        # Generate angle sines vector
        A = np.linspace(start=self._start, stop=1, num=self._augmentation_factor)
        
        # Calculate adjacent values using Pythagorean theorem
        V = np.sqrt(np.maximum(np.square(W/A.T) - np.square(W), 0))  # Use maximum to avoid negative values
        VR = np.flip(V, axis=1)
        
        # Apply selected interpolation equation
        interpolation_func = self._equations[self._equation]
        Y = np.apply_along_axis(
            lambda x: interpolation_func(x, x.max() if x.max() > self._zero_threshold else 1.0),
            axis=1,
            arr=VR
        )
        
        # Calculate final interpolated points
        X1 = X[:-1].reshape(-1, 1)
        Y1 = Y * W + X1
        
        # Restore zero regions
        Y1[zero_diff_mask.flatten()] = X1[zero_diff_mask.flatten()]
        
        return Y1.flatten()

    def interpolate_matrix(self) -> np.ndarray:
        """Interpolate all vectors in the input matrix.
        
        Returns:
            np.ndarray: Matrix with all vectors interpolated.
        """
        return np.array([
            self.interpolate_vector(x) for x in self._X
        ])

    def arr(self) -> np.ndarray:
        """Get interpolated data as a numpy array.
        
        Returns:
            np.ndarray: Interpolated data.
        """
        if self._X.ndim == 1:
            return self.interpolate_vector(self._X)
        return self.interpolate_matrix()

    def pd_frame(
        self,
        save: bool = False,
        output_path: Union[str, None] = None,
        index: bool = False
    ) -> pd.DataFrame:
        """Get interpolated data as a pandas DataFrame.
        
        Args:
            save: Whether to save the DataFrame to disk.
            output_path: Path where to save the DataFrame. If None and save=True,
                        uses 'New_dataframe.xlsx' in current directory.
            index: Whether to include index in the output file.
                        
        Returns:
            pd.DataFrame: Interpolated data with original column names.
            
        Raises:
            ValueError: If save=True and output_path is invalid.
        """
        output = pd.DataFrame(self.arr()).T
        output.columns = self._input.columns
        
        if save:
            if output_path is None:
                output_path = 'New_dataframe.xlsx'
            try:
                output.to_excel(output_path, index=index)
            except Exception as e:
                raise ValueError(f"Failed to save DataFrame: {str(e)}")
        
        return output
    
    @property
    def input_data(self) -> pd.DataFrame:
        """Get the input DataFrame."""
        return self._input
    
    @property
    def equation(self) -> str:
        """Get the current interpolation equation."""
        return self._equation
    
    @property
    def augmentation_factor(self) -> int:
        """Get the augmentation factor."""
        return self._augmentation_factor
    
    @property
    def precision(self) -> int:
        """Get the numerical precision."""
        return self._precision
    
    @property
    def zero_threshold(self) -> float:
        """Get the zero threshold value."""
        return self._zero_threshold
    
    @classmethod
    def available_equations(cls) -> set:
        """Get the set of available interpolation equations.
        
        Returns:
            set: Available equation names.
        """
        return cls.VALID_EQUATIONS.copy()
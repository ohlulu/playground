"""
Base strategy class that provides common functionality for all trading strategies.
"""

from abc import ABC, abstractmethod
from typing import Dict, Optional
import pandas as pd
import numpy as np
import logging

logger = logging.getLogger(__name__)

class Strategy(ABC):
    """
    Abstract base class for all trading strategies.
    Provides basic technical analysis functionality.
    """
    
    def __init__(self):
        """Initialize strategy with default parameters."""
        pass
    
    @abstractmethod
    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        """
        Analyze market data and generate trading signals.
        
        Args:
            df: DataFrame containing market data with OHLCV columns
            
        Returns:
            Dictionary containing analysis results, or None if analysis fails
        """
        try:
            # Calculate basic technical indicators
            df = self._calculate_basic_indicators(df)
            
            # Generate basic trading signal
            signal = self._generate_basic_signal(df)
            
            return {
                'signal': signal,
                'indicators': {
                    'sma_20': df['sma_20'].iloc[-1],
                    'sma_50': df['sma_50'].iloc[-1],
                    'rsi': df['rsi'].iloc[-1],
                    'macd': df['macd'].iloc[-1],
                    'macd_signal': df['macd_signal'].iloc[-1]
                }
            }
        except Exception as e:
            logger.error(f"Error in basic analysis: {str(e)}")
            return None
    
    def _calculate_basic_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Calculate basic technical indicators."""
        # Simple Moving Averages
        df['sma_20'] = df['close'].rolling(window=20).mean()
        df['sma_50'] = df['close'].rolling(window=50).mean()
        
        # RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # MACD
        exp1 = df['close'].ewm(span=12, adjust=False).mean()
        exp2 = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = exp1 - exp2
        df['macd_signal'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        return df
    
    def _generate_basic_signal(self, df: pd.DataFrame) -> float:
        """
        Generate basic trading signal based on technical indicators.
        
        Returns:
            Signal value between -1 and 1
            -1: Strong sell signal
             0: Neutral
             1: Strong buy signal
        """
        signals = []
        
        # Moving Average Crossover
        if df['sma_20'].iloc[-1] > df['sma_50'].iloc[-1]:
            signals.append(1)
        else:
            signals.append(-1)
        
        # RSI
        rsi = df['rsi'].iloc[-1]
        if rsi < 30:
            signals.append(1)  # Oversold
        elif rsi > 70:
            signals.append(-1)  # Overbought
        else:
            signals.append(0)
        
        # MACD
        if df['macd'].iloc[-1] > df['macd_signal'].iloc[-1]:
            signals.append(1)
        else:
            signals.append(-1)
        
        # Combine signals
        final_signal = np.mean(signals)
        
        return np.clip(final_signal, -1, 1) 
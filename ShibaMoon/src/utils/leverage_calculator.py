import pandas as pd
import numpy as np
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

class LeverageCalculator:
    def __init__(self, max_leverage: int = 10, base_leverage: int = 5):
        self.max_leverage = max_leverage
        self.base_leverage = base_leverage
        
    def calculate_futures_leverage(self, df: pd.DataFrame, trend_score: float) -> int:
        """
        計算期貨交易的槓桿倍數
        
        參數：
        - df: 價格數據
        - trend_score: 趨勢強度分數 (0-1)
        
        考慮因素：
        1. 波動率（ATR）
        2. 趨勢強度
        3. 成交量穩定性
        4. 市場深度
        5. 價格穩定性
        """
        try:
            # 1. 波動率評分 (0-1)
            volatility_score = self._calculate_volatility_score(df)
            
            # 2. 成交量穩定性評分 (0-1)
            volume_score = self._calculate_volume_stability_score(df)
            
            # 3. 價格穩定性評分 (0-1)
            price_stability_score = self._calculate_price_stability_score(df)
            
            # 4. 市場深度評分 (0-1)
            market_depth_score = self._calculate_market_depth_score(df)
            
            # 綜合評分 (0-1)
            weights = {
                'volatility': 0.3,
                'volume': 0.2,
                'price_stability': 0.2,
                'market_depth': 0.15,
                'trend': 0.15
            }
            
            total_score = (
                volatility_score * weights['volatility'] +
                volume_score * weights['volume'] +
                price_stability_score * weights['price_stability'] +
                market_depth_score * weights['market_depth'] +
                trend_score * weights['trend']
            )
            
            # 計算建議槓桿
            leverage = self.base_leverage + round(total_score * (self.max_leverage - self.base_leverage))
            
            return min(max(leverage, self.base_leverage), self.max_leverage)
            
        except Exception as e:
            logger.warning(f"Error calculating futures leverage: {str(e)}")
            return self.base_leverage
            
    def calculate_grid_leverage(self, df: pd.DataFrame) -> int:
        """
        計算網格交易的槓桿倍數
        
        網格交易需要更保守的槓桿策略，主要考慮：
        1. 波動率穩定性
        2. 價格區間穩定性
        3. 成交量穩定性
        """
        try:
            # 1. 波動率穩定性 (0-1)
            volatility_stability = self._calculate_volatility_stability(df)
            
            # 2. 價格區間穩定性 (0-1)
            price_range_stability = self._calculate_price_range_stability(df)
            
            # 3. 成交量穩定性 (0-1)
            volume_stability = self._calculate_volume_stability_score(df)
            
            # 綜合評分
            weights = {
                'volatility_stability': 0.4,
                'price_range_stability': 0.4,
                'volume_stability': 0.2
            }
            
            total_score = (
                volatility_stability * weights['volatility_stability'] +
                price_range_stability * weights['price_range_stability'] +
                volume_stability * weights['volume_stability']
            )
            
            # 網格交易使用更保守的槓桿
            max_grid_leverage = min(self.max_leverage, 7)
            leverage = self.base_leverage + round(total_score * (max_grid_leverage - self.base_leverage))
            
            return min(max(leverage, self.base_leverage), max_grid_leverage)
            
        except Exception as e:
            logger.warning(f"Error calculating grid leverage: {str(e)}")
            return self.base_leverage

    def _calculate_volatility_score(self, df: pd.DataFrame) -> float:
        """計算波動率評分"""
        try:
            # 使用 ATR 相對值
            recent_atr = df['atr'].tail(20).mean()
            current_atr = df['atr'].iloc[-1]
            atr_ratio = current_atr / recent_atr if recent_atr > 0 else 1.0
            
            if atr_ratio <= 0.8:
                return 1.0  # 低波動
            elif atr_ratio <= 1.2:
                return 0.8  # 正常波動
            elif atr_ratio <= 1.5:
                return 0.5  # 高波動
            else:
                return 0.2  # 極高波動
                
        except Exception as e:
            logger.warning(f"Error in volatility calculation: {str(e)}")
            return 0.5

    def _calculate_volume_stability_score(self, df: pd.DataFrame) -> float:
        """計算成交量穩定性評分"""
        try:
            # 計算成交量的變異係數
            recent_volume = df['volume'].tail(20)
            cv = recent_volume.std() / recent_volume.mean() if recent_volume.mean() > 0 else 1.0
            
            if cv < 0.5:
                return 1.0  # 非常穩定
            elif cv < 1.0:
                return 0.8  # 穩定
            elif cv < 1.5:
                return 0.5  # 較不穩定
            else:
                return 0.2  # 不穩定
                
        except Exception as e:
            logger.warning(f"Error in volume stability calculation: {str(e)}")
            return 0.5

    def _calculate_price_stability_score(self, df: pd.DataFrame) -> float:
        """計算價格穩定性評分"""
        try:
            # 使用布林帶寬度
            bb_width = (df['bb_high'].iloc[-1] - df['bb_low'].iloc[-1]) / df['bb_mid'].iloc[-1]
            
            if bb_width < 0.02:
                return 1.0  # 非常穩定
            elif bb_width < 0.04:
                return 0.8  # 穩定
            elif bb_width < 0.06:
                return 0.5  # 較不穩定
            else:
                return 0.2  # 不穩定
                
        except Exception as e:
            logger.warning(f"Error in price stability calculation: {str(e)}")
            return 0.5

    def _calculate_market_depth_score(self, df: pd.DataFrame) -> float:
        """計算市場深度評分（基於成交量）"""
        try:
            # 使用最近成交量相對於平均成交量的比例
            avg_volume = df['volume'].tail(20).mean()
            current_volume = df['volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume if avg_volume > 0 else 1.0
            
            if volume_ratio > 1.5:
                return 1.0  # 深度好
            elif volume_ratio > 1.0:
                return 0.8  # 深度正常
            elif volume_ratio > 0.5:
                return 0.5  # 深度較差
            else:
                return 0.2  # 深度差
                
        except Exception as e:
            logger.warning(f"Error in market depth calculation: {str(e)}")
            return 0.5

    def _calculate_volatility_stability(self, df: pd.DataFrame) -> float:
        """計算波動率的穩定性（專用於網格交易）"""
        try:
            # 計算 ATR 的穩定性
            recent_atr = df['atr'].tail(20)
            atr_cv = recent_atr.std() / recent_atr.mean() if recent_atr.mean() > 0 else 1.0
            
            if atr_cv < 0.3:
                return 1.0  # 非常穩定
            elif atr_cv < 0.5:
                return 0.8  # 穩定
            elif atr_cv < 0.7:
                return 0.5  # 較不穩定
            else:
                return 0.2  # 不穩定
                
        except Exception as e:
            logger.warning(f"Error in volatility stability calculation: {str(e)}")
            return 0.5

    def _calculate_price_range_stability(self, df: pd.DataFrame) -> float:
        """計算價格區間的穩定性（專用於網格交易）"""
        try:
            # 使用布林帶的穩定性
            bb_width = (df['bb_high'] - df['bb_low']) / df['bb_mid']
            bb_width_cv = bb_width.tail(20).std() / bb_width.tail(20).mean()
            
            if bb_width_cv < 0.2:
                return 1.0  # 非常穩定
            elif bb_width_cv < 0.4:
                return 0.8  # 穩定
            elif bb_width_cv < 0.6:
                return 0.5  # 較不穩定
            else:
                return 0.2  # 不穩定
                
        except Exception as e:
            logger.warning(f"Error in price range stability calculation: {str(e)}")
            return 0.5 
import pandas as pd
import numpy as np
from typing import Dict, Optional, Tuple
from .base import Strategy
import logging
from src.utils.leverage_calculator import LeverageCalculator

logger = logging.getLogger(__name__)

class GridStrategy(Strategy):
    def __init__(self):
        self.leverage_calculator = LeverageCalculator()

    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        try:
            last_row = df.iloc[-1]
            current_price = last_row['close']
            
            # 計算波動率
            volatility = self._calculate_volatility(df)
            if volatility is None:
                return None
                
            # 計算網格參數
            grid_params = self._calculate_grid_parameters(df, volatility)
            if grid_params is None:
                return None
                
            # 使用新的槓桿計算器
            leverage = self.leverage_calculator.calculate_grid_leverage(df)
            
            # 計算網格的方向偏好
            direction_score = self._calculate_direction_score(df)
            grid_type = 'neutral'
            if direction_score > 0.5:
                grid_type = 'long_bias'
            elif direction_score < -0.5:
                grid_type = 'short_bias'
                
            return {
                'current_price': current_price,
                'grid_type': grid_type,
                'direction_score': direction_score,
                'volatility': volatility,
                'leverage': leverage,
                'grid_parameters': grid_params,
                'score': self._calculate_strategy_score(df, volatility)
            }
        except Exception as e:
            logger.error(f"Error in grid strategy analysis: {str(e)}")
            return None
        
    def _calculate_volatility(self, df: pd.DataFrame) -> Optional[float]:
        """計算波動率"""
        try:
            last_row = df.iloc[-1]
            atr = last_row['atr']
            price = last_row['close']
            return (atr / price) * 100  # 轉換為百分比
        except (KeyError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating volatility: {str(e)}")
            return None
        
    def _calculate_grid_parameters(self, df: pd.DataFrame, volatility: float) -> Optional[Dict]:
        """計算網格參數"""
        try:
            last_row = df.iloc[-1]
            current_price = last_row['close']
            
            # 使用布林帶來決定網格範圍
            upper_price = last_row['bb_high']
            lower_price = last_row['bb_low']
            
            # 根據槓桿值調整網格範圍
            range_adjustment = 1.0 + (0.01 * (self.leverage_calculator.base_leverage - 2))  # 每增加 1 倍槓桿增加 1% 的範圍
            
            # 如果價格已經接近布林帶邊緣，擴大範圍
            if current_price > last_row['bb_mid']:
                upper_price = upper_price * range_adjustment
                lower_price = last_row['bb_mid'] * (2 - range_adjustment)
            else:
                upper_price = last_row['bb_mid'] * range_adjustment
                lower_price = lower_price * (2 - range_adjustment)
                
            # 根據波動率和槓桿決定網格數量
            if volatility < 1:  # 低波動
                grid_number = 6
            elif volatility < 2:  # 中等波動
                grid_number = 8
            else:  # 高波動
                grid_number = 12
                
            # 計算每個網格的價差
            grid_spacing = (upper_price - lower_price) / grid_number
            
            # 計算每個網格的投資金額（假設總投資 7000 USDT）
            investment_per_grid = 7000 / grid_number
            
            return {
                'upper_price': upper_price,
                'lower_price': lower_price,
                'grid_number': grid_number,
                'grid_spacing': grid_spacing,
                'investment_per_grid': investment_per_grid,
                'price_precision': self._calculate_price_precision(current_price),
                'quantity_precision': 3  # 默認數量精度為3位
            }
        except Exception as e:
            logger.warning(f"Error calculating grid parameters: {str(e)}")
            return None
        
    def _calculate_strategy_score(self, df: pd.DataFrame, volatility: float) -> float:
        """計算策略評分"""
        # 檢查是否處於區間震盪
        is_ranging = self._is_market_ranging(df)
        
        # 檢查流動性
        liquidity_score = self._calculate_liquidity_score(df)
        
        # 波動率評分
        volatility_score = 1.0
        if volatility > 3:
            volatility_score = max(0.3, 1 - (volatility - 3) * 0.2)
            
        # 綜合評分
        score = (0.4 * is_ranging + 0.3 * liquidity_score + 0.3 * volatility_score)
        return min(1.0, score)
        
    def _is_market_ranging(self, df: pd.DataFrame) -> float:
        """判斷是否處於區間震盪"""
        # 使用 ADX 判斷趨勢強度，ADX 低表示區間震盪
        # 這裡用 RSI 的波動範圍來簡單判斷
        rsi = df['rsi'].tail(20)
        rsi_range = rsi.max() - rsi.min()
        
        if rsi_range < 20:  # RSI 波動小，可能在區間震盪
            return 1.0
        elif rsi_range < 30:
            return 0.7
        else:
            return 0.3
            
    def _calculate_liquidity_score(self, df: pd.DataFrame) -> float:
        """計算流動性評分"""
        recent_volume = df['volume'].tail(20).mean()
        volume_std = df['volume'].tail(20).std()
        
        # 計算變異係數
        cv = volume_std / recent_volume
        
        if cv < 0.5:  # 成交量穩定
            return 1.0
        elif cv < 1.0:
            return 0.7
        else:
            return 0.4
            
    def _calculate_direction_score(self, df: pd.DataFrame) -> float:
        """計算方向分數"""
        last_row = df.iloc[-1]
        
        # 使用多個指標綜合判斷
        signals = []
        
        # 1. EMA 方向
        signals.append(1 if last_row['ema_20'] > last_row['ema_50'] else -1)
        
        # 2. RSI 位置
        rsi = last_row['rsi']
        if rsi > 70:
            signals.append(-1)
        elif rsi < 30:
            signals.append(1)
        else:
            signals.append(0)
            
        # 3. 布林通道位置
        bb_position = (last_row['close'] - last_row['bb_mid']) / (last_row['bb_high'] - last_row['bb_mid'])
        if bb_position > 0.8:
            signals.append(-1)
        elif bb_position < -0.8:
            signals.append(1)
        else:
            signals.append(0)
            
        return sum(signals) / len(signals)
        
    def _calculate_price_precision(self, price: float) -> int:
        """計算價格精度"""
        if price < 0.1:
            return 6
        elif price < 1:
            return 5
        elif price < 10:
            return 4
        elif price < 100:
            return 3
        elif price < 1000:
            return 2
        else:
            return 1 
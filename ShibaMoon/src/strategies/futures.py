import pandas as pd
import numpy as np
from typing import Dict, Optional
from .base import Strategy
from src.utils.leverage_calculator import LeverageCalculator
import logging

logger = logging.getLogger(__name__)

class FuturesStrategy(Strategy):
    def __init__(self):
        self.leverage_calculator = LeverageCalculator()

    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        try:
            last_row = df.iloc[-1]
            price = last_row['close']
            
            signals = self._calculate_signals(df)
            weights = {
                'trend_score': 0.3,      # 趨勢信號權重增加
                'momentum_score': 0.2,    # 動能
                'volatility_score': 0.2,  # 波動
                'volume_score': 0.3       # 成交量信號權重增加
            }
            
            # Calculate directional score (-1 to 1, negative means short)
            direction_score = self._calculate_direction_score(df)
            
            # Calculate absolute score (0 to 1)
            abs_score = sum(score * weights[signal] for signal, score in signals.items())
            
            # Only proceed if the absolute score is high enough
            if abs_score >= 0.7:  # 期貨要求更高的確信度
                # 使用新的槓桿計算器
                leverage = self.leverage_calculator.calculate_futures_leverage(
                    df=df,
                    trend_score=abs(direction_score)  # 使用方向分數的絕對值作為趨勢強度
                )
                
                # Determine position type
                position_type = 'long' if direction_score > 0 else 'short'
                
                # 根據槓桿值動態調整止損和獲利比例
                # 槓桿越高，止損越緊，獲利目標相應調整
                stop_loss_percentage = 0.01 + (0.005 * (leverage - 5))  # 基礎 1% + 每增加 1 倍槓桿增加 0.5%
                take_profit_percentage = stop_loss_percentage * 3  # 維持 1:3 的風險收益比
                
                # Calculate stop loss and take profit based on position type
                stop_loss = price * (1 - stop_loss_percentage) if position_type == 'long' else price * (1 + stop_loss_percentage)
                take_profit = price * (1 + take_profit_percentage) if position_type == 'long' else price * (1 - take_profit_percentage)
                
                return {
                    'current_price': price,
                    'position_type': position_type,
                    'stop_loss': stop_loss,
                    'take_profit': take_profit,
                    'leverage': leverage,
                    'margin': 7000 / leverage,
                    'signals': signals,
                    'score': abs_score,
                    'direction_score': direction_score
                }
            return None
            
        except Exception as e:
            logger.error(f"Error in futures strategy analysis: {str(e)}")
            return None

    def _calculate_signals(self, df: pd.DataFrame) -> Dict[str, float]:
        last_row = df.iloc[-1]
        return {
            'trend_score': self._calculate_trend_score(df),
            'momentum_score': self._calculate_momentum_score(df),
            'volatility_score': self._calculate_volatility_score(df),
            'volume_score': self._calculate_volume_score(df)
        }

    def _calculate_trend_score(self, df: pd.DataFrame) -> float:
        """
        趨勢評分規則：
        1. EMA 20/50 交叉
        2. MACD 信號
        """
        last_row = df.iloc[-1]
        
        # EMA 趨勢得分
        ema_trend = 1 if last_row['ema_20'] > last_row['ema_50'] else 0
        
        # MACD 得分
        macd_score = 0.5
        if last_row['macd'] > last_row['macd_signal']:
            macd_score = min(1.0, 0.5 + (last_row['macd'] - last_row['macd_signal']) * 15)
        else:
            macd_score = max(0.0, 0.5 - (last_row['macd_signal'] - last_row['macd']) * 15)
        
        return 0.5 * ema_trend + 0.5 * macd_score

    def _calculate_momentum_score(self, df: pd.DataFrame) -> float:
        """
        動能評分規則：
        1. RSI 值
        2. ROC 值
        """
        last_row = df.iloc[-1]
        
        # RSI 評分
        rsi = last_row['rsi']
        if 40 <= rsi <= 60:
            rsi_score = 1.0 - abs(50 - rsi) / 20
        elif 30 <= rsi <= 70:
            rsi_score = 0.7 - abs(50 - rsi) / 40
        else:
            rsi_score = max(0.0, 0.3 - abs(50 - rsi) / 50)
        
        # ROC 評分
        roc = last_row['roc']
        roc_score = 0.5 + min(max(roc * 0.1, -0.5), 0.5)  # 將 ROC 值轉換為 0-1 分數
        
        return 0.6 * rsi_score + 0.4 * roc_score

    def _calculate_volatility_score(self, df: pd.DataFrame) -> float:
        """
        波動率評分規則：
        1. 布林帶位置
        2. ATR 相對值
        """
        last_row = df.iloc[-1]
        
        try:
            # 布林帶評分
            bb_range = last_row['bb_high'] - last_row['bb_low']
            bb_position = (last_row['close'] - last_row['bb_mid']) / bb_range
            
            if bb_position <= 0.2:  # 接近下軌
                bb_score = 0.8
            elif bb_position >= 0.8:  # 接近上軌
                bb_score = 0.3
            else:
                bb_score = 1.0 - abs(0.5 - bb_position)
            
            # ATR 評分
            recent_atr = df['atr'].tail(20).mean()
            atr_ratio = last_row['atr'] / recent_atr if recent_atr > 0 else 1.0
            
            if 0.5 <= atr_ratio <= 1.5:
                atr_score = 1.0
            elif 1.5 < atr_ratio <= 2.0:
                atr_score = 0.7
            elif 0.3 <= atr_ratio < 0.5:
                atr_score = 0.5
            else:
                atr_score = 0.3
            
            return 0.6 * bb_score + 0.4 * atr_score
            
        except (KeyError, ZeroDivisionError) as e:
            logger.warning(f"Error calculating volatility score: {str(e)}")
            return 0.5  # 返回中性分數

    def _calculate_volume_score(self, df: pd.DataFrame) -> float:
        """
        成交量評分規則：
        1. 成交量趨勢
        2. VWAP 距離
        """
        last_row = df.iloc[-1]
        
        # 成交量趨勢評分
        volume_trend = 1 if last_row['volume'] > last_row['volume_ema'] else 0
        
        # VWAP 距離評分
        vwap_distance = abs(last_row['vwap_distance'])
        if vwap_distance <= 1.0:
            vwap_score = 1.0
        elif 1.0 < vwap_distance <= 3.0:
            vwap_score = 1.0 - (vwap_distance - 1.0) / 2
        else:
            vwap_score = max(0.0, 0.5 - (vwap_distance - 3.0) / 10)
        
        return 0.4 * volume_trend + 0.6 * vwap_score

    def _calculate_direction_score(self, df: pd.DataFrame) -> float:
        """
        計算方向分數，範圍從 -1 到 1
        負值表示做空信號，正值表示做多信號
        """
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
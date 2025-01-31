import pandas as pd
from typing import Dict, Optional
from .base import Strategy
import logging

logger = logging.getLogger(__name__)

class SpotStrategy(Strategy):
    def analyze(self, df: pd.DataFrame) -> Optional[Dict]:
        last_row = df.iloc[-1]
        price = last_row['close']
        
        signals = self._calculate_signals(df)
        weights = {
            'trend_score': 0.25,     # 趨勢
            'momentum_score': 0.25,   # 動能
            'volatility_score': 0.25, # 波動
            'volume_score': 0.25      # 成交量
        }
        score = sum(score * weights[signal] for signal, score in signals.items())
        
        if score >= 0.65:  # 現貨可以接受較低的確信度
            return {
                'current_price': price,
                'stop_loss': price * 0.95,  # 5% 止損
                'take_profit': price * 1.1,  # 10% 獲利
                'position_size': self._calculate_position_size(df),
                'signals': signals,
                'score': score
            }
        return None

    def _calculate_signals(self, df: pd.DataFrame) -> Dict[str, float]:
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
        1. RSI 值（主要指標）
        2. ROC 值（輔助指標）
        """
        last_row = df.iloc[-1]
        
        # RSI 評分（現貨策略對超買超賣更敏感）
        rsi = last_row['rsi']
        if 45 <= rsi <= 55:
            rsi_score = 1.0
        elif 35 <= rsi <= 65:
            rsi_score = 0.8 - abs(50 - rsi) / 30
        elif rsi < 30 or rsi > 70:  # 超買超賣區域也可能是機會
            rsi_score = 0.6
        else:
            rsi_score = 0.4
        
        # ROC 評分（用於確認趨勢強度）
        roc = last_row['roc']
        if roc > 0:
            roc_score = min(1.0, 0.5 + roc * 0.1)  # 正 ROC，上漲趨勢
        else:
            roc_score = max(0.0, 0.5 + roc * 0.1)  # 負 ROC，下跌趨勢
        
        # 現貨交易更重視 RSI，ROC 作為輔助
        return 0.8 * rsi_score + 0.2 * roc_score

    def _calculate_volatility_score(self, df: pd.DataFrame) -> float:
        """
        波動率評分規則：
        1. 布林帶位置（主要參考）
        2. ATR 相對值（輔助參考）
        """
        last_row = df.iloc[-1]
        
        try:
            # 布林帶評分（現貨策略更關注超買超賣）
            bb_range = last_row['bb_high'] - last_row['bb_low']
            bb_position = (last_row['close'] - last_row['bb_low']) / bb_range
            
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
        
        # VWAP 距離評分（現貨策略對價格偏離更敏感）
        vwap_distance = last_row['vwap_distance']
        if abs(vwap_distance) <= 0.5:
            vwap_score = 1.0
        elif abs(vwap_distance) <= 2.0:
            vwap_score = 0.8
        elif vwap_distance < -2.0:  # 低於 VWAP
            vwap_score = 0.6
        else:
            vwap_score = 0.3
        
        return 0.3 * volume_trend + 0.7 * vwap_score

    def _calculate_position_size(self, df: pd.DataFrame) -> float:
        """
        計算建議倉位大小（相對於總資金的百分比）
        基於波動率和趨勢強度
        """
        last_row = df.iloc[-1]
        
        # 使用 ATR 來評估風險
        recent_atr = df['atr'].tail(20).mean()
        atr_ratio = last_row['atr'] / recent_atr
        
        # 基礎倉位
        if atr_ratio <= 0.8:
            base_size = 0.3  # 低波動時可以較大倉位
        elif 0.8 < atr_ratio <= 1.2:
            base_size = 0.2  # 正常波動
        else:
            base_size = 0.1  # 高波動時降低倉位
        
        # 根據趨勢強度調整
        trend_strength = self._calculate_trend_score(df)
        size_adj = trend_strength * 0.1  # 最多增加 10% 倉位
        
        return min(base_size + size_adj, 0.4)  # 最大倉位 40% 
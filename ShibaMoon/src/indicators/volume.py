import pandas as pd
import ta
from .base import Indicator

class VolumeIndicator(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df['volume_ema'] = ta.trend.EMAIndicator(df['volume'], window=20).ema_indicator()
        return df

    def get_name(self) -> str:
        return "Volume"

class VWAPIndicator(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        # Calculate VWAP
        df['vwap'] = (df['volume'] * (df['high'] + df['low'] + df['close']) / 3).cumsum() / df['volume'].cumsum()
        
        # Calculate distance from VWAP
        df['vwap_distance'] = ((df['close'] - df['vwap']) / df['vwap']) * 100
        return df

    def get_name(self) -> str:
        return "VWAP" 
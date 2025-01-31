import pandas as pd
import ta
from .base import Indicator

class RSIIndicator(Indicator):
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df['rsi'] = ta.momentum.RSIIndicator(df['close'], window=self.period).rsi()
        return df

    def get_name(self) -> str:
        return f"RSI_{self.period}"

class MACDIndicator(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        macd = ta.trend.MACD(df['close'])
        df['macd'] = macd.macd()
        df['macd_signal'] = macd.macd_signal()
        return df

    def get_name(self) -> str:
        return "MACD"

class ROCIndicator(Indicator):
    def __init__(self, period: int = 12):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        df['roc'] = ta.momentum.ROCIndicator(df['close'], window=self.period).roc()
        return df

    def get_name(self) -> str:
        return f"ROC_{self.period}" 
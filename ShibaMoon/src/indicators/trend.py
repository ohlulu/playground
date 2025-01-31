import pandas as pd
import ta
from .base import Indicator

class BollingerBandsIndicator(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        bollinger = ta.volatility.BollingerBands(df['close'])
        df['bb_high'] = bollinger.bollinger_hband()
        df['bb_low'] = bollinger.bollinger_lband()
        df['bb_mid'] = bollinger.bollinger_mavg()
        return df

    def get_name(self) -> str:
        return "BollingerBands"

class MovingAverageIndicator(Indicator):
    def __init__(self, periods: list = [5, 10, 20, 50, 200]):
        self.periods = periods

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        for period in self.periods:
            df[f'sma_{period}'] = ta.trend.sma_indicator(df['close'], window=period)
            df[f'ema_{period}'] = ta.trend.ema_indicator(df['close'], window=period)
        return df

    def get_name(self) -> str:
        return f"MA_{','.join(map(str, self.periods))}"

class ParabolicSARIndicator(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        psar = ta.trend.PSARIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close']
        )
        df['psar'] = psar.psar()
        df['psar_up'] = psar.psar_up()
        df['psar_down'] = psar.psar_down()
        return df

    def get_name(self) -> str:
        return "ParabolicSAR"

class ADXIndicator(Indicator):
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        adx = ta.trend.ADXIndicator(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.period
        )
        df['adx'] = adx.adx()
        df['adx_pos'] = adx.adx_pos()
        df['adx_neg'] = adx.adx_neg()
        return df

    def get_name(self) -> str:
        return f"ADX_{self.period}"

class IchimokuIndicator(Indicator):
    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        ichimoku = ta.trend.IchimokuIndicator(
            high=df['high'],
            low=df['low']
        )
        df['ichimoku_a'] = ichimoku.ichimoku_a()
        df['ichimoku_b'] = ichimoku.ichimoku_b()
        df['ichimoku_base'] = ichimoku.ichimoku_base_line()
        df['ichimoku_conv'] = ichimoku.ichimoku_conversion_line()
        return df

    def get_name(self) -> str:
        return "Ichimoku"

class ATRIndicator(Indicator):
    def __init__(self, period: int = 14):
        self.period = period

    def calculate(self, df: pd.DataFrame) -> pd.DataFrame:
        atr = ta.volatility.AverageTrueRange(
            high=df['high'],
            low=df['low'],
            close=df['close'],
            window=self.period
        )
        df['atr'] = atr.average_true_range()
        return df

    def get_name(self) -> str:
        return f"ATR_{self.period}" 
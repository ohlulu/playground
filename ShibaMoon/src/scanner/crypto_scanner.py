import ccxt
import pandas as pd
from typing import Dict, List, Optional
import logging
from tqdm import tqdm
from src.indicators import (
    MovingAverageIndicator,
    MACDIndicator,
    RSIIndicator,
    ROCIndicator,
    BollingerBandsIndicator,
    ATRIndicator,
    VolumeIndicator,
    VWAPIndicator
)
from src.strategies import SpotStrategy, FuturesStrategy, GridStrategy
from src.utils.reporting import ReportGenerator
import os

logger = logging.getLogger(__name__)

class CryptoScanner:
    def __init__(self):
        self.exchange = ccxt.binance({'enableRateLimit': True})
        self.timeframe = '6h' # '1m', '5m', '15m', '30m', '1h', '2h', '4h', '6h', '12h', '1d'
        self.limit = 500 # 獲取 500 根 K 線
        
        # 共用的基礎指標
        self.base_indicators = {
            'volume': VolumeIndicator(),
            'vwap': VWAPIndicator(),
            'bb': BollingerBandsIndicator(),  # 所有策略都需要布林帶
            'atr': ATRIndicator(period=14)    # 所有策略都需要 ATR
        }
        
        # 現貨策略指標
        self.spot_indicators = {
            **self.base_indicators,
            'ema': MovingAverageIndicator(periods=[20, 50]),
            'macd': MACDIndicator(),
            'rsi': RSIIndicator(period=14),
            'roc': ROCIndicator(period=12)
        }
        
        # 合約策略指標
        self.futures_indicators = {
            **self.base_indicators,
            'ema': MovingAverageIndicator(periods=[20, 50]),
            'macd': MACDIndicator(),
            'rsi': RSIIndicator(period=14),
            'roc': ROCIndicator(period=12)
        }
        
        # 網格策略指標
        self.grid_indicators = {
            **self.base_indicators,
            'ema': MovingAverageIndicator(periods=[20, 50]),  # 用於方向判斷
            'rsi': RSIIndicator(period=14)                    # 用於判斷區間震盪
        }
        
        # 初始化策略
        self.strategies = {
            'spot': SpotStrategy(),
            'futures': FuturesStrategy(),
            'grid': GridStrategy()
        }
        self.report_generator = ReportGenerator()

    def fetch_ohlcv(self, symbol: str) -> Optional[pd.DataFrame]:
        try:
            ohlcv = self.exchange.fetch_ohlcv(symbol, self.timeframe, limit=self.limit)
            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df['symbol'] = symbol
            return df
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None

    def calculate_indicators(self, df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        根據不同策略計算不同的指標
        """
        dfs = {}
        
        # 為每個策略計算對應的指標
        spot_df = df.copy()
        futures_df = df.copy()
        grid_df = df.copy()
        
        # 計算現貨指標
        for name, indicator in self.spot_indicators.items():
            spot_df = indicator.calculate(spot_df)
            
        # 計算合約指標
        for name, indicator in self.futures_indicators.items():
            futures_df = indicator.calculate(futures_df)
            
        # 計算網格指標
        for name, indicator in self.grid_indicators.items():
            grid_df = indicator.calculate(grid_df)
            
        return {
            'spot': spot_df,
            'futures': futures_df,
            'grid': grid_df
        }

    def analyze_market(self, dfs: Dict[str, pd.DataFrame]) -> Dict:
        """
        使用對應的 DataFrame 分析每個策略
        """
        results = {}
        for strategy_name, strategy in self.strategies.items():
            try:
                results[strategy_name] = strategy.analyze(dfs[strategy_name])
            except Exception as e:
                logger.error(f"Error analyzing {strategy_name}: {str(e)}")
                results[strategy_name] = None
        return results

    def scan_market(self, output_json: bool = True) -> List[Dict]:
        markets = self.exchange.load_markets()
        # Filter out stablecoins
        stablecoins = ['USDT', 'USDC', 'BUSD', 'DAI', 'TUSD', 'UST', 'USDP', 'USDD']
        usdt_pairs = [
            symbol for symbol in markets.keys() 
            if symbol.endswith('/USDT') and 
            not any(stablecoin in symbol.split('/')[0] for stablecoin in stablecoins)
        ]
        
        opportunities = []
        
        # 使用 tqdm 顯示進度條
        for symbol in tqdm(usdt_pairs[:100], desc="Analyzing markets", ncols=100):
            df = self.fetch_ohlcv(symbol)
            if df is None:
                continue
                
            strategy_dfs = self.calculate_indicators(df)
            analysis = self.analyze_market(strategy_dfs)
            
            if any(result for result in analysis.values() if result is not None):
                opportunities.append({
                    'symbol': symbol,
                    **analysis
                })

        self.report_generator.generate_report(opportunities, output_json=output_json)
        logger.info(f"✨ Market analysis completed successfully! Found {len(opportunities)} opportunities.")
        return opportunities 
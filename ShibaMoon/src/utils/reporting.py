import json
from pathlib import Path
from typing import List, Dict
from datetime import datetime
import numpy as np

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.bool_):
            return bool(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

class ReportGenerator:
    def __init__(self, base_dir: str = "reports"):
        self.reports_dir = Path(base_dir)
        self.reports_dir.mkdir(exist_ok=True)

    def generate_report(self, opportunities: List[Dict], output_json: bool = True) -> None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Save detailed JSON report only if output_json is True
        if output_json:
            self._save_detailed_report(opportunities, timestamp)
        
        # Generate summary report
        self._save_summary_report(opportunities, timestamp)

    def _save_detailed_report(self, opportunities: List[Dict], timestamp: str) -> None:
        detailed_report = {
            'timestamp': timestamp,
            'opportunities': opportunities
        }
        with open(self.reports_dir / f"detailed_report_{timestamp}.json", 'w') as f:
            json.dump(detailed_report, f, indent=2, cls=CustomJSONEncoder)

    def _save_summary_report(self, opportunities: List[Dict], timestamp: str) -> None:
        summary = self._generate_summary_report(opportunities)
        with open(self.reports_dir / f"summary_report_{timestamp}.txt", 'w') as f:
            f.write(summary)

    def _generate_summary_report(self, opportunities: List[Dict]) -> str:
        summary = []
        summary.append("=== Top 10 Crypto Investment Opportunities ===\n")
        
        # Sort opportunities by score (highest first)
        sorted_opportunities = sorted(
            opportunities,
            key=lambda x: max(
                x['spot']['score'] if x['spot'] else 0,
                x['futures']['score'] if x['futures'] else 0,
                x['grid']['score'] if x['grid'] else 0
            ),
            reverse=True
        )
        
        # Only take top 10
        for opp in sorted_opportunities[:10]:
            summary.append(f"\nSymbol: {opp['symbol']}")
            
            # 只顯示評分高於 0.8 的策略
            if opp['spot'] and opp['spot']['score'] >= 0.8:
                summary.append("\n1. Spot Trading Opportunity:")
                summary.append(f"Price: ${opp['spot']['current_price']:.4f}")
                summary.append(f"Score: {opp['spot']['score']:.2f}")
                summary.append("Signals:")
                for signal, value in opp['spot']['signals'].items():
                    summary.append(f"  - {signal}: {'✓' if value else '✗'}")

            if opp['futures'] and opp['futures']['score'] >= 0.8:
                summary.append("\n2. Futures Trading Opportunity:")
                summary.append(f"Price: ${opp['futures']['current_price']:.4f}")
                summary.append(f"Position: {opp['futures']['position_type'].upper()}")
                summary.append(f"Score: {opp['futures']['score']:.2f}")
                summary.append(f"Direction Score: {opp['futures']['direction_score']:.2f}")
                summary.append(f"Suggested Leverage: {opp['futures']['leverage']}x")
                summary.append(f"Stop Loss: ${opp['futures']['stop_loss']:.4f}")
                summary.append(f"Take Profit: ${opp['futures']['take_profit']:.4f}")
                summary.append("Signals:")
                for signal, value in opp['futures']['signals'].items():
                    summary.append(f"  - {signal}: {'✓' if value else '✗'}")

            if opp['grid'] and opp['grid']['score'] >= 0.8:
                summary.append("\n3. Grid Trading Opportunity:")
                summary.append(f"Price: ${opp['grid']['current_price']:.4f}")
                summary.append(f"Score: {opp['grid']['score']:.2f}")
                summary.append(f"Grid Type: {opp['grid']['grid_type'].upper()}")
                summary.append(f"Direction Score: {opp['grid']['direction_score']:.2f}")
                summary.append(f"Volatility: {opp['grid']['volatility']:.2f}%")
                summary.append(f"Suggested Leverage: {opp['grid']['leverage']}x")
                
                # Grid Parameters
                grid_params = opp['grid']['grid_parameters']
                summary.append("\nGrid Parameters:")
                summary.append(f"  - Upper Price: ${grid_params['upper_price']:.4f}")
                summary.append(f"  - Lower Price: ${grid_params['lower_price']:.4f}")
                summary.append(f"  - Grid Number: {grid_params['grid_number']}")
                summary.append(f"  - Grid Spacing: ${grid_params['grid_spacing']:.4f}")
                summary.append(f"  - Investment per Grid: ${grid_params['investment_per_grid']:.2f}")
                summary.append(f"  - Price Precision: {grid_params['price_precision']}")
                summary.append(f"  - Quantity Precision: {grid_params['quantity_precision']}")

            summary.append("\n" + "="*50)

        # Add timestamp at the bottom
        summary.append(f"\nGenerated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return "\n".join(summary) 
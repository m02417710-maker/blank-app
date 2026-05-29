"""
EGX Pro Terminal v27 - Advanced Formatters
Professional data formatting for reports and displays
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime

class DataFormatter:
    @staticmethod
    def format_stock_table(df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
        if df.empty:
            return df

        if columns:
            df = df[columns]

        formatted = df.copy()

        for col in formatted.columns:
            if 'price' in col.lower() or 'close' in col.lower() or 'open' in col.lower():
                formatted[col] = formatted[col].apply(lambda x: f"{x:.2f}" if pd.notna(x) else "N/A")
            elif 'change_pct' in col.lower() or 'pct' in col.lower():
                formatted[col] = formatted[col].apply(
                    lambda x: f"{x:+.2f}%" if pd.notna(x) else "N/A"
                )
            elif 'volume' in col.lower():
                formatted[col] = formatted[col].apply(
                    lambda x: f"{x/1e6:.2f}M" if pd.notna(x) and x >= 1e6 else 
                              f"{x/1e3:.2f}K" if pd.notna(x) and x >= 1e3 else 
                              f"{x:.0f}" if pd.notna(x) else "N/A"
                )
            elif 'market_cap' in col.lower():
                formatted[col] = formatted[col].apply(
                    lambda x: f"{x/1e9:.2f}B" if pd.notna(x) and x >= 1e9 else 
                              f"{x/1e6:.2f}M" if pd.notna(x) else "N/A"
                )

        return formatted

    @staticmethod
    def format_indicator_value(value: float, indicator_type: str = "default") -> str:
        if pd.isna(value):
            return "N/A"

        formats = {
            "price": f"{value:.2f}",
            "percentage": f"{value:.2f}%",
            "ratio": f"{value:.3f}",
            "index": f"{value:.1f}",
            "volume": f"{value:,.0f}",
            "default": f"{value:.2f}"
        }
        return formats.get(indicator_type, formats["default"])

    @staticmethod
    def color_code_value(value: float, threshold_positive: float = 0, 
                         threshold_negative: float = 0) -> str:
        if value > threshold_positive:
            return f"<span style='color: #4caf50'>{value:+.2f}</span>"
        elif value < threshold_negative:
            return f"<span style='color: #f44336'>{value:+.2f}</span>"
        else:
            return f"<span style='color: #ff9800'>{value:+.2f}</span>"

    @staticmethod
    def format_backtest_result(result: Dict) -> Dict[str, str]:
        return {
            "Total Return": f"{result.get('total_return_pct', 0):+.2f}%",
            "Sharpe Ratio": f"{result.get('sharpe_ratio', 0):.3f}",
            "Sortino Ratio": f"{result.get('sortino_ratio', 0):.3f}",
            "Max Drawdown": f"{result.get('max_drawdown_pct', 0):.2f}%",
            "Calmar Ratio": f"{result.get('calmar_ratio', 0):.3f}",
            "Win Rate": f"{result.get('win_rate', 0):.1f}%",
            "Profit Factor": f"{result.get('profit_factor', 0):.3f}",
            "Total Trades": str(result.get('total_trades', 0)),
            "Avg Win": f"{result.get('avg_win', 0):.2f}%",
            "Avg Loss": f"{result.get('avg_loss', 0):.2f}%",
            "VaR (95%)": f"{result.get('var_95', 0):.3f}%",
            "CVaR (95%)": f"{result.get('cvar_95', 0):.3f}%"
        }

    @staticmethod
    def format_prediction_result(prediction: Any) -> Dict[str, str]:
        return {
            "Direction": prediction.predicted_direction,
            "Confidence": f"{prediction.confidence:.0%}",
            "Target Price": f"{prediction.target_price:.2f} EGP",
            "Stop Loss": f"{prediction.stop_loss:.2f} EGP",
            "Expected Return": f"{prediction.expected_return:+.2f}%",
            "Risk/Reward": f"1:{prediction.risk_reward_ratio:.1f}",
            "Sharpe Estimate": f"{prediction.sharpe_estimate:.2f}",
            "Prob Up": f"{prediction.probability_up:.1%}",
            "Prob Down": f"{prediction.probability_down:.1%}",
            "Prob Sideways": f"{prediction.probability_sideways:.1%}"
        }

formatter = DataFormatter()

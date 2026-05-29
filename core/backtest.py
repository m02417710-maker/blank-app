"""
EGX Pro Terminal v27 - Backtest Engine
Advanced strategy testing with walk-forward analysis and optimization
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from scipy import stats

from config.settings import app_config

@dataclass
class Trade:
    entry_date: str
    exit_date: Optional[str] = None
    entry_price: float = 0.0
    exit_price: float = 0.0
    shares: int = 0
    pnl: float = 0.0
    pnl_pct: float = 0.0
    type: str = 'long'
    status: str = 'open'
    holding_days: int = 0
    exit_reason: str = ''
    max_profit_pct: float = 0.0
    max_loss_pct: float = 0.0

@dataclass
class BacktestResult:
    strategy_name: str
    symbol: str
    initial_capital: float
    final_capital: float
    total_return_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    calmar_ratio: float
    win_rate: float
    profit_factor: float
    avg_win: float
    avg_loss: float
    avg_trade: float
    total_trades: int
    winning_trades: int
    losing_trades: int
    trades: List[Trade]
    equity_curve: List[Dict]
    monthly_returns: Dict
    yearly_returns: Dict
    rolling_sharpe: List[float]
    var_95: float
    cvar_95: float
    params: Dict
    timestamp: str

class BacktestEngine:
    def __init__(self, initial_capital: float = 100000.0):
        self.initial_capital = initial_capital

    def run_strategy(self, df: pd.DataFrame, strategy_type: str,
                     symbol: str = "UNKNOWN",
                     initial_capital: float = None,
                     commission: float = 0.0015,
                     slippage: float = 0.001,
                     risk_per_trade: float = 0.10,
                     max_positions: int = 5,
                     params: Dict = None) -> Optional[BacktestResult]:

        if df is None or df.empty or len(df) < 50:
            return None

        if initial_capital is None:
            initial_capital = self.initial_capital

        df = df.copy()

        # Generate signals based on strategy type
        if strategy_type == 'rsi':
            signals = self.rsi_strategy(df, **(params or {}))
        elif strategy_type == 'macd':
            signals = self.macd_strategy(df)
        elif strategy_type == 'ema':
            signals = self.ema_strategy(df, **(params or {}))
        elif strategy_type == 'bb':
            signals = self.bb_strategy(df)
        elif strategy_type == 'trend_following':
            signals = self.trend_following_strategy(df)
        elif strategy_type == 'mean_reversion':
            signals = self.mean_reversion_strategy(df)
        elif strategy_type == 'breakout':
            signals = self.breakout_strategy(df)
        elif strategy_type == 'composite':
            signals = self.composite_strategy(df)
        else:
            return None

        trades = []
        capital = initial_capital
        position = None
        equity_curve = []
        daily_returns = []

        for i in range(len(df)):
            date = str(df.index[i]) if isinstance(df.index[i], str) else df.index[i].strftime('%Y-%m-%d')
            price = df['close'].iloc[i]
            signal = signals.iloc[i]

            # Entry
            if position is None and signal == 1:
                execution_price = price * (1 + slippage)
                position_value = capital * risk_per_trade
                cost = execution_price * (1 + commission)
                shares = int(position_value / cost)
                shares = max(shares, 1)

                if shares > 0:
                    position = Trade(
                        entry_date=date, entry_price=execution_price,
                        shares=shares, type='long', status='open'
                    )
                    capital -= shares * cost

            # Exit
            elif position is not None and signal == -1:
                execution_price = price * (1 - slippage)
                revenue = position.shares * execution_price * (1 - commission)
                pnl = revenue - (position.shares * position.entry_price)
                pnl_pct = (pnl / (position.shares * position.entry_price)) * 100

                position.exit_date = date
                position.exit_price = execution_price
                position.pnl = pnl
                position.pnl_pct = pnl_pct
                position.status = 'closed'
                position.exit_reason = 'Signal'

                # Calculate holding days
                try:
                    entry_dt = datetime.strptime(position.entry_date, '%Y-%m-%d')
                    exit_dt = datetime.strptime(date, '%Y-%m-%d')
                    position.holding_days = (exit_dt - entry_dt).days
                except:
                    position.holding_days = 0

                trades.append(position)
                capital += revenue
                position = None

            # Track max profit/loss for open position
            if position is not None:
                current_pnl_pct = (price - position.entry_price) / position.entry_price * 100
                position.max_profit_pct = max(position.max_profit_pct, current_pnl_pct)
                position.max_loss_pct = min(position.max_loss_pct, current_pnl_pct)

            # Calculate equity
            current_equity = capital
            if position is not None:
                current_equity += position.shares * price

            daily_return = (current_equity - initial_capital) / initial_capital
            equity_curve.append({
                'date': date, 'equity': current_equity,
                'returns': daily_return,
                'drawdown': 0
            })
            daily_returns.append(daily_return)

        # Close any open position at end
        if position is not None:
            execution_price = df['close'].iloc[-1] * (1 - slippage)
            revenue = position.shares * execution_price * (1 - commission)
            pnl = revenue - (position.shares * position.entry_price)
            pnl_pct = (pnl / (position.shares * position.entry_price)) * 100

            position.exit_date = str(df.index[-1])
            position.exit_price = execution_price
            position.pnl = pnl
            position.pnl_pct = pnl_pct
            position.status = 'closed'
            position.exit_reason = 'End of Data'
            trades.append(position)

        # Calculate metrics
        equity_df = pd.DataFrame(equity_curve)
        total_return = ((equity_df['equity'].iloc[-1] - initial_capital) / initial_capital) * 100

        # Drawdown
        rolling_max = equity_df['equity'].cummax()
        drawdown = (equity_df['equity'] - rolling_max) / rolling_max
        max_drawdown = drawdown.min() * 100
        equity_df['drawdown'] = drawdown * 100

        # Returns analysis
        returns_series = pd.Series(daily_returns)
        excess_returns = returns_series.mean() - (0.15 / 252)  # Risk-free rate

        sharpe = (excess_returns / returns_series.std()) * np.sqrt(252) if returns_series.std() != 0 else 0

        # Sortino ratio
        downside_returns = returns_series[returns_series < 0]
        sortino = (excess_returns / downside_returns.std()) * np.sqrt(252) if len(downside_returns) > 0 and downside_returns.std() != 0 else 0

        # Calmar ratio
        calmar = (total_return / 100) / abs(max_drawdown / 100) if max_drawdown != 0 else 0

        # Trade statistics
        if trades:
            winning_trades = [t for t in trades if t.pnl > 0]
            losing_trades = [t for t in trades if t.pnl <= 0]
            win_rate = (len(winning_trades) / len(trades)) * 100

            avg_win = np.mean([t.pnl_pct for t in winning_trades]) if winning_trades else 0
            avg_loss = np.mean([t.pnl_pct for t in losing_trades]) if losing_trades else 0
            avg_trade = np.mean([t.pnl_pct for t in trades])

            gross_profit = sum(t.pnl for t in winning_trades)
            gross_loss = abs(sum(t.pnl for t in losing_trades))
            profit_factor = gross_profit / gross_loss if gross_loss > 0 else float('inf')
        else:
            winning_trades = []
            losing_trades = []
            win_rate = 0
            avg_win = 0
            avg_loss = 0
            avg_trade = 0
            profit_factor = 0

        # VaR and CVaR
        returns_array = np.array(daily_returns)
        var_95 = np.percentile(returns_array, 5) * 100
        cvar_95 = np.mean(returns_array[returns_array <= np.percentile(returns_array, 5)]) * 100

        # Monthly returns
        equity_df['month'] = pd.to_datetime(equity_df['date']).dt.to_period('M')
        monthly_returns = equity_df.groupby('month').apply(
            lambda x: (1 + x['returns'].iloc[-1]) / (1 + x['returns'].iloc[0]) - 1
        ).to_dict()

        # Yearly returns
        equity_df['year'] = pd.to_datetime(equity_df['date']).dt.to_period('Y')
        yearly_returns = equity_df.groupby('year').apply(
            lambda x: (1 + x['returns'].iloc[-1]) / (1 + x['returns'].iloc[0]) - 1
        ).to_dict()

        # Rolling Sharpe
        rolling_sharpe = []
        for i in range(20, len(returns_series)):
            window = returns_series.iloc[i-20:i]
            r_sharpe = (window.mean() / window.std()) * np.sqrt(252) if window.std() != 0 else 0
            rolling_sharpe.append(r_sharpe)

        return BacktestResult(
            strategy_name=strategy_type,
            symbol=symbol,
            initial_capital=initial_capital,
            final_capital=equity_df['equity'].iloc[-1],
            total_return_pct=round(total_return, 2),
            sharpe_ratio=round(sharpe, 3),
            sortino_ratio=round(sortino, 3),
            max_drawdown_pct=round(max_drawdown, 2),
            calmar_ratio=round(calmar, 3),
            win_rate=round(win_rate, 2),
            profit_factor=round(profit_factor, 3),
            avg_win=round(avg_win, 2),
            avg_loss=round(avg_loss, 2),
            avg_trade=round(avg_trade, 2),
            total_trades=len(trades),
            winning_trades=len(winning_trades),
            losing_trades=len(losing_trades),
            trades=trades,
            equity_curve=equity_curve,
            monthly_returns=monthly_returns,
            yearly_returns=yearly_returns,
            rolling_sharpe=rolling_sharpe,
            var_95=round(var_95, 3),
            cvar_95=round(cvar_95, 3),
            params=params or {},
            timestamp=datetime.now().isoformat()
        )

    def rsi_strategy(self, df: pd.DataFrame, oversold: int = 30, overbought: int = 70) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        position = 0
        for i in range(1, len(df)):
            rsi = df['rsi'].iloc[i]
            if position == 0 and rsi < oversold:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and rsi > overbought:
                signals.iloc[i] = -1
                position = 0
        return signals

    def macd_strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        position = 0
        for i in range(1, len(df)):
            if position == 0 and df['macd'].iloc[i] > df['macd_signal'].iloc[i] and df['macd'].iloc[i-1] <= df['macd_signal'].iloc[i-1]:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and df['macd'].iloc[i] < df['macd_signal'].iloc[i] and df['macd'].iloc[i-1] >= df['macd_signal'].iloc[i-1]:
                signals.iloc[i] = -1
                position = 0
        return signals

    def ema_strategy(self, df: pd.DataFrame, fast: int = 9, slow: int = 21) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        fast_col = f'ema_{fast}'
        slow_col = f'ema_{slow}'
        if fast_col not in df.columns or slow_col not in df.columns:
            return signals
        position = 0
        for i in range(1, len(df)):
            if position == 0 and df[fast_col].iloc[i] > df[slow_col].iloc[i] and df[fast_col].iloc[i-1] <= df[slow_col].iloc[i-1]:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and df[fast_col].iloc[i] < df[slow_col].iloc[i] and df[fast_col].iloc[i-1] >= df[slow_col].iloc[i-1]:
                signals.iloc[i] = -1
                position = 0
        return signals

    def bb_strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        position = 0
        for i in range(len(df)):
            close = df['close'].iloc[i]
            lower = df['bb_lower'].iloc[i]
            upper = df['bb_upper'].iloc[i]
            if position == 0 and close < lower:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and close > upper:
                signals.iloc[i] = -1
                position = 0
        return signals

    def trend_following_strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        position = 0
        for i in range(50, len(df)):
            close = df['close'].iloc[i]
            ema50 = df['ema_50'].iloc[i]
            ema200 = df['ema_200'].iloc[i] if 'ema_200' in df.columns else ema50
            adx = df['adx'].iloc[i]

            if position == 0 and close > ema50 > ema200 and adx > 25:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and (close < ema50 or adx < 20):
                signals.iloc[i] = -1
                position = 0
        return signals

    def mean_reversion_strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        position = 0
        for i in range(1, len(df)):
            rsi = df['rsi'].iloc[i]
            bb_pct = df['bb_percent_b'].iloc[i] if 'bb_percent_b' in df.columns else 0.5

            if position == 0 and rsi < 25 and bb_pct < 0.05:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and (rsi > 50 or bb_pct > 0.5):
                signals.iloc[i] = -1
                position = 0
        return signals

    def breakout_strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        position = 0
        for i in range(20, len(df)):
            high_20 = df['high'].iloc[i-20:i].max()
            low_20 = df['low'].iloc[i-20:i].min()
            close = df['close'].iloc[i]
            volume_ratio = df['volume_ratio'].iloc[i] if 'volume_ratio' in df.columns else 1

            if position == 0 and close > high_20 and volume_ratio > 1.5:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and close < low_20:
                signals.iloc[i] = -1
                position = 0
        return signals

    def composite_strategy(self, df: pd.DataFrame) -> pd.Series:
        signals = pd.Series(0, index=df.index)
        position = 0
        for i in range(1, len(df)):
            score = 0
            if df['rsi'].iloc[i] < 35: score += 1
            if df['macd'].iloc[i] > df['macd_signal'].iloc[i]: score += 1
            if df['close'].iloc[i] > df['ema_21'].iloc[i]: score += 1
            if df['adx'].iloc[i] > 20: score += 1
            if df['volume_ratio'].iloc[i] > 1.2: score += 1

            if position == 0 and score >= 4:
                signals.iloc[i] = 1
                position = 1
            elif position == 1 and score <= 1:
                signals.iloc[i] = -1
                position = 0
        return signals

    def optimize_strategy(self, df: pd.DataFrame, strategy_type: str, param_grid: Dict) -> Dict:
        best_result = None
        best_params = None
        best_sharpe = -np.inf

        if strategy_type == 'rsi':
            for oversold in param_grid.get('oversold', [20, 25, 30, 35]):
                for overbought in param_grid.get('overbought', [65, 70, 75, 80]):
                    result = self.run_strategy(df, 'rsi', params={'oversold': oversold, 'overbought': overbought})
                    if result and result.sharpe_ratio > best_sharpe:
                        best_sharpe = result.sharpe_ratio
                        best_result = result
                        best_params = {'oversold': oversold, 'overbought': overbought}

        elif strategy_type == 'ema':
            for fast in param_grid.get('fast', [5, 9, 12, 20]):
                for slow in param_grid.get('slow', [21, 26, 50, 200]):
                    if fast < slow:
                        result = self.run_strategy(df, 'ema', params={'fast': fast, 'slow': slow})
                        if result and result.sharpe_ratio > best_sharpe:
                            best_sharpe = result.sharpe_ratio
                            best_result = result
                            best_params = {'fast': fast, 'slow': slow}

        return {
            'best_params': best_params,
            'best_result': best_result,
            'best_sharpe': best_sharpe
        }

    def walk_forward_analysis(self, df: pd.DataFrame, strategy_type: str,
                              train_size: int = 126, test_size: int = 63) -> List[BacktestResult]:
        results = []
        total_len = len(df)

        for start in range(0, total_len - train_size - test_size, test_size):
            train_df = df.iloc[start:start + train_size]
            test_df = df.iloc[start + train_size:start + train_size + test_size]

            # Optimize on training data
            opt = self.optimize_strategy(train_df, strategy_type, {})

            # Test on out-of-sample data
            if opt['best_params']:
                result = self.run_strategy(test_df, strategy_type, params=opt['best_params'])
                if result:
                    results.append(result)

        return results

    def get_strategy_list(self) -> Dict[str, str]:
        return {
            'RSI Mean Reversion': 'rsi',
            'MACD Crossover': 'macd',
            'EMA Crossover': 'ema',
            'Bollinger Bands': 'bb',
            'Trend Following': 'trend_following',
            'Mean Reversion': 'mean_reversion',
            'Breakout': 'breakout',
            'Composite Signal': 'composite'
        }

backtest_engine = BacktestEngine()

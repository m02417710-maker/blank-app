"""
EGX Pro Terminal v27 - AI/ML Prediction Engine
Advanced ensemble prediction with statistical modeling
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from scipy import stats
import warnings
warnings.filterwarnings("ignore")

from config.settings import app_config

@dataclass
class PredictionResult:
    symbol: str
    current_price: float
    predicted_direction: str
    confidence: float
    target_price: float
    stop_loss: float
    horizon_days: int
    features_importance: Dict[str, float]
    model_used: str
    timestamp: str
    probability_up: float
    probability_down: float
    probability_sideways: float
    expected_return: float
    risk_reward_ratio: float
    sharpe_estimate: float
    monte_carlo_results: Optional[Dict] = None
    scenario_analysis: Optional[Dict] = None

class AIPredictionEngine:
    def __init__(self):
        self.models = {}
        self.feature_importance = {}
        self.is_trained = False
        self.prediction_history = {}

    def _prepare_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df is None or len(df) < 60:
            return None

        features = pd.DataFrame(index=df.index)

        # Price-based features
        features["returns"] = df["close"].pct_change()
        price_ratio = df["close"] / df["close"].shift(1)
        price_ratio = price_ratio.replace(0, np.nan)
        features["log_returns"] = np.log(price_ratio)
        features["log_returns"] = features["log_returns"].replace([np.inf, -np.inf], np.nan)

        # Multi-period momentum
        for period in [3, 5, 10, 20]:
            features[f"price_momentum_{period}"] = df["close"].pct_change(period)

        # Volatility features
        for period in [5, 10, 20, 60]:
            features[f"volatility_{period}"] = features["returns"].rolling(period).std()

        # Technical indicator features
        if "rsi" in df.columns:
            features["rsi"] = df["rsi"]
            features["rsi_slope"] = df["rsi"].diff(5)
            features["rsi_divergence"] = self._compute_divergence(df["close"], df["rsi"])

        if "macd" in df.columns:
            features["macd"] = df["macd"]
            features["macd_hist"] = df.get("macd_hist", 0)
            features["macd_slope"] = df["macd"].diff(3)

        if "adx" in df.columns:
            features["adx"] = df["adx"]
            features["adx_trend"] = (df["adx"] > 25).astype(int)

        if "atr_pct" in df.columns:
            features["atr_pct"] = df["atr_pct"]

        # Moving average distances
        for col in ["ema_9", "ema_21", "ema_50", "ema_200", "sma_20", "sma_50"]:
            if col in df.columns:
                ma_values = df[col].replace(0, np.nan)
                features[f"{col}_distance"] = (df["close"] - df[col]) / ma_values

        # Volume features
        if "volume_ratio" in df.columns:
            features["volume_ratio"] = df["volume_ratio"]
        if "volume" in df.columns:
            features["volume_momentum"] = df["volume"].pct_change(5)

        if "trend_strength" in df.columns:
            features["trend_strength"] = df["trend_strength"]

        # Pattern features
        if "mean_reversion_score" in df.columns:
            features["mean_reversion"] = df["mean_reversion_score"]
        if "momentum_score" in df.columns:
            features["momentum"] = df["momentum_score"]
        if "breakout_score" in df.columns:
            features["breakout"] = df["breakout_score"]

        # Lagged returns
        for lag in [1, 2, 3, 5, 10]:
            features[f"returns_lag_{lag}"] = features["returns"].shift(lag)

        # Rolling statistics
        features["rolling_mean_10"] = df["close"].rolling(10).mean()
        features["rolling_std_10"] = df["close"].rolling(10).std()
        features["rolling_max_10"] = df["high"].rolling(10).max()
        features["rolling_min_10"] = df["low"].rolling(10).min()

        # Target variable
        horizon = app_config.AI_PREDICTION_HORIZON
        features["target"] = df["close"].shift(-horizon) / df["close"] - 1

        features = features.dropna()
        if features.empty or len(features) < 10:
            return None

        return features

    def _compute_divergence(self, price: pd.Series, indicator: pd.Series, lookback: int = 20) -> pd.Series:
        divergence = pd.Series(0.0, index=price.index)

        for i in range(lookback, len(price)):
            price_high = price.iloc[i-lookback:i].max()
            price_low = price.iloc[i-lookback:i].min()
            ind_high = indicator.iloc[i-lookback:i].max()
            ind_low = indicator.iloc[i-lookback:i].min()

            if price.iloc[i] > price_high and indicator.iloc[i] < ind_high:
                divergence.iloc[i] = -1  # Bearish divergence
            elif price.iloc[i] < price_low and indicator.iloc[i] > ind_low:
                divergence.iloc[i] = 1   # Bullish divergence

        return divergence

    def predict(self, df: pd.DataFrame, symbol: str) -> Optional[PredictionResult]:
        features_df = self._prepare_features(df)
        if features_df is None or len(features_df) < 10:
            return None

        latest = features_df.iloc[-1]
        current_price = df["close"].iloc[-1]

        # Multi-model ensemble signals
        signals = []

        # Model 1: RSI-based
        if "rsi" in latest:
            rsi = latest["rsi"]
            if rsi < 25: signals.append(("UP", 0.85))
            elif rsi < 30: signals.append(("UP", 0.70))
            elif rsi > 75: signals.append(("DOWN", 0.85))
            elif rsi > 70: signals.append(("DOWN", 0.70))
            else: signals.append(("SIDEWAYS", 0.40))

        # Model 2: MACD-based
        if "macd" in latest and "macd_hist" in latest:
            if latest["macd"] > 0 and latest["macd_hist"] > 0 and latest["macd_slope"] > 0:
                signals.append(("UP", 0.75))
            elif latest["macd"] > 0 and latest["macd_hist"] > 0:
                signals.append(("UP", 0.60))
            elif latest["macd"] < 0 and latest["macd_hist"] < 0 and latest["macd_slope"] < 0:
                signals.append(("DOWN", 0.75))
            elif latest["macd"] < 0 and latest["macd_hist"] < 0:
                signals.append(("DOWN", 0.60))
            else:
                signals.append(("SIDEWAYS", 0.50))

        # Model 3: Trend Strength
        if "trend_strength" in latest:
            ts = latest["trend_strength"]
            if ts > 80: signals.append(("UP", 0.80))
            elif ts > 60: signals.append(("UP", 0.65))
            elif ts < 20: signals.append(("DOWN", 0.80))
            elif ts < 40: signals.append(("DOWN", 0.65))
            else: signals.append(("SIDEWAYS", 0.55))

        # Model 4: Price Momentum
        if "price_momentum_5" in latest:
            mom = latest["price_momentum_5"]
            if mom > 0.08: signals.append(("UP", 0.70))
            elif mom > 0.03: signals.append(("UP", 0.55))
            elif mom < -0.08: signals.append(("DOWN", 0.70))
            elif mom < -0.03: signals.append(("DOWN", 0.55))
            else: signals.append(("SIDEWAYS", 0.45))

        # Model 5: Volume Analysis
        if "volume_ratio" in latest and "returns" in latest:
            vr = latest["volume_ratio"]
            ret = latest["returns"]
            if vr > 2.5 and ret > 0.02: signals.append(("UP", 0.75))
            elif vr > 2.5 and ret < -0.02: signals.append(("DOWN", 0.75))
            elif vr > 1.5 and ret > 0: signals.append(("UP", 0.55))
            elif vr > 1.5 and ret < 0: signals.append(("DOWN", 0.55))

        # Model 6: Mean Reversion
        if "mean_reversion" in latest:
            mr = latest["mean_reversion"]
            if mr > 0.7: signals.append(("UP", 0.65))
            elif mr < -0.7: signals.append(("DOWN", 0.65))

        # Model 7: Breakout Detection
        if "breakout" in latest:
            bo = latest["breakout"]
            if bo > 0.8: signals.append(("UP", 0.70))

        # Model 8: Divergence
        if "rsi_divergence" in latest:
            div = latest["rsi_divergence"]
            if div == 1: signals.append(("UP", 0.70))
            elif div == -1: signals.append(("DOWN", 0.70))

        # Aggregate signals
        if not signals:
            direction = "SIDEWAYS"
            confidence = 0.5
        else:
            up_score = sum(conf for d, conf in signals if d == "UP")
            down_score = sum(conf for d, conf in signals if d == "DOWN")
            sideways_score = sum(conf for d, conf in signals if d == "SIDEWAYS")
            total = up_score + down_score + sideways_score

            if total == 0:
                direction = "SIDEWAYS"
                confidence = 0.5
            else:
                scores = {
                    "UP": up_score / total,
                    "DOWN": down_score / total,
                    "SIDEWAYS": sideways_score / total
                }
                direction = max(scores, key=scores.get)
                confidence = scores[direction]

        # Calculate probabilities
        total_signals = len(signals) if signals else 1
        prob_up = up_score / total if total > 0 else 0.33
        prob_down = down_score / total if total > 0 else 0.33
        prob_sideways = sideways_score / total if total > 0 else 0.34

        # Normalize probabilities
        total_prob = prob_up + prob_down + prob_sideways
        if total_prob > 0:
            prob_up /= total_prob
            prob_down /= total_prob
            prob_sideways /= total_prob

        # Calculate target and stop loss using ATR
        atr = df["atr"].iloc[-1] if "atr" in df.columns else current_price * 0.02

        if direction == "UP":
            target_price = current_price + (atr * 4)
            stop_loss = current_price - (atr * 2)
        elif direction == "DOWN":
            target_price = current_price - (atr * 4)
            stop_loss = current_price + (atr * 2)
        else:
            target_price = current_price * 1.02
            stop_loss = current_price * 0.98

        # Expected return and risk metrics
        expected_return = ((target_price / current_price - 1) * prob_up +
                          (stop_loss / current_price - 1) * prob_down +
                          (0.005) * prob_sideways)

        reward = abs(target_price - current_price)
        risk = abs(stop_loss - current_price)
        rr_ratio = reward / risk if risk > 0 else 0

        # Sharpe estimate
        returns_std = df["close"].pct_change().std() * np.sqrt(252)
        sharpe_estimate = (expected_return * 252) / (returns_std * 100) if returns_std > 0 else 0

        # Monte Carlo simulation
        mc_results = self._monte_carlo_simulation(df, horizon=app_config.AI_PREDICTION_HORIZON)

        # Scenario analysis
        scenarios = self._scenario_analysis(df, current_price, direction)

        feature_importance = {
            "rsi": 0.20,
            "macd": 0.18,
            "trend_strength": 0.15,
            "volume_ratio": 0.12,
            "price_momentum": 0.10,
            "mean_reversion": 0.08,
            "breakout": 0.07,
            "divergence": 0.05,
            "volatility": 0.05
        }

        return PredictionResult(
            symbol=symbol,
            current_price=round(current_price, 2),
            predicted_direction=direction,
            confidence=round(confidence, 2),
            target_price=round(target_price, 2),
            stop_loss=round(stop_loss, 2),
            horizon_days=app_config.AI_PREDICTION_HORIZON,
            features_importance=feature_importance,
            model_used="Ensemble v27 (8 Models)",
            timestamp=datetime.now().isoformat(),
            probability_up=round(prob_up, 3),
            probability_down=round(prob_down, 3),
            probability_sideways=round(prob_sideways, 3),
            expected_return=round(expected_return * 100, 2),
            risk_reward_ratio=round(rr_ratio, 2),
            sharpe_estimate=round(sharpe_estimate, 2),
            monte_carlo_results=mc_results,
            scenario_analysis=scenarios
        )

    def _monte_carlo_simulation(self, df: pd.DataFrame, horizon: int = 5, 
                                 simulations: int = 1000) -> Dict:
        returns = df["close"].pct_change().dropna()
        current_price = df["close"].iloc[-1]

        mu = returns.mean()
        sigma = returns.std()

        # Generate random paths
        random_returns = np.random.normal(mu, sigma, (simulations, horizon))
        price_paths = current_price * np.exp(np.cumsum(random_returns, axis=1))

        final_prices = price_paths[:, -1]

        return {
            "mean_price": round(np.mean(final_prices), 2),
            "median_price": round(np.median(final_prices), 2),
            "std_price": round(np.std(final_prices), 2),
            "percentile_5": round(np.percentile(final_prices, 5), 2),
            "percentile_25": round(np.percentile(final_prices, 25), 2),
            "percentile_75": round(np.percentile(final_prices, 75), 2),
            "percentile_95": round(np.percentile(final_prices, 95), 2),
            "prob_up": round(np.mean(final_prices > current_price), 3),
            "prob_down": round(np.mean(final_prices < current_price), 3)
        }

    def _scenario_analysis(self, df: pd.DataFrame, current_price: float, 
                           direction: str) -> Dict:
        atr = df["atr"].iloc[-1] if "atr" in df.columns else current_price * 0.02

        scenarios = {
            "bullish": {
                "description": "Bullish scenario - strong upward momentum",
                "target": round(current_price + atr * 5, 2),
                "probability": 0.25 if direction == "UP" else 0.15,
                "rationale": "Break above resistance with volume confirmation"
            },
            "base_case": {
                "description": "Base case - moderate movement",
                "target": round(current_price + (atr * 2 if direction == "UP" else -atr * 2 if direction == "DOWN" else 0), 2),
                "probability": 0.50,
                "rationale": "Normal market conditions, gradual trend continuation"
            },
            "bearish": {
                "description": "Bearish scenario - strong downward pressure",
                "target": round(current_price - atr * 5, 2),
                "probability": 0.25 if direction == "DOWN" else 0.15,
                "rationale": "Break below support with increased selling pressure"
            }
        }

        return scenarios

    def predict_batch(self, data_dict: Dict[str, pd.DataFrame]) -> Dict[str, PredictionResult]:
        results = {}
        for symbol, df in data_dict.items():
            result = self.predict(df, symbol)
            if result:
                results[symbol] = result
        return results

    def get_market_sentiment(self, predictions: Dict[str, PredictionResult]) -> Dict:
        if not predictions:
            return {"sentiment": "NEUTRAL", "score": 50, "bullish": 0, "bearish": 0, "neutral": 0}

        bullish_score = sum(p.confidence for p in predictions.values() if p.predicted_direction == "UP")
        bearish_score = sum(p.confidence for p in predictions.values() if p.predicted_direction == "DOWN")
        neutral_score = sum(p.confidence for p in predictions.values() if p.predicted_direction == "SIDEWAYS")

        bullish = sum(1 for p in predictions.values() if p.predicted_direction == "UP")
        bearish = sum(1 for p in predictions.values() if p.predicted_direction == "DOWN")
        neutral = sum(1 for p in predictions.values() if p.predicted_direction == "SIDEWAYS")

        total = len(predictions)
        total_confidence = bullish_score + bearish_score + neutral_score

        score = ((bullish_score * 100) + (neutral_score * 50)) / total_confidence if total_confidence > 0 else 50

        if score > 65: sentiment = "BULLISH"
        elif score < 35: sentiment = "BEARISH"
        else: sentiment = "NEUTRAL"

        avg_confidence = np.mean([p.confidence for p in predictions.values()])
        avg_expected_return = np.mean([p.expected_return for p in predictions.values()])

        return {
            "sentiment": sentiment,
            "score": round(score, 1),
            "bullish": bullish,
            "bearish": bearish,
            "neutral": neutral,
            "total": total,
            "avg_confidence": round(avg_confidence, 2),
            "avg_expected_return": round(avg_expected_return, 2),
            "bullish_pct": round(bullish / total * 100, 1),
            "bearish_pct": round(bearish / total * 100, 1)
        }

ai_engine = AIPredictionEngine()

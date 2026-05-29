"""
EGX Pro Terminal v27 - Chart Engine
Advanced charting with Plotly - Institutional-grade visuals
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict

class ChartEngine:
    def create_main_chart(self, df: pd.DataFrame, symbol: str,
                          indicators: List[str] = None,
                          show_volume: bool = True,
                          show_patterns: bool = False) -> go.Figure:
        if indicators is None:
            indicators = ['ema_9', 'ema_21', 'ema_50']

        rows = 3 if show_volume else 2
        row_heights = [0.6, 0.25, 0.15] if show_volume else [0.7, 0.3]

        fig = make_subplots(
            rows=rows, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=row_heights,
            subplot_titles=(f'{symbol} Price', 'RSI', 'Volume') if show_volume else (f'{symbol} Price', 'RSI')
        )

        x_vals = df['date'] if 'date' in df.columns else df.index

        # Candlestick
        fig.add_trace(go.Candlestick(
            x=x_vals, open=df['open'], high=df['high'],
            low=df['low'], close=df['close'],
            name='Price', increasing_line_color='#00ff88',
            decreasing_line_color='#ff4444'
        ), row=1, col=1)

        # Indicators
        colors = {'ema_9': '#ffaa00', 'ema_21': '#00aaff', 'ema_50': '#ff00ff',
                  'ema_200': '#ffffff', 'sma_20': '#ff6600', 'sma_50': '#66ff00',
                  'sma_200': '#cccccc', 'vwap': '#ff69b4'}

        for ind in indicators:
            if ind in df.columns:
                fig.add_trace(go.Scatter(
                    x=x_vals, y=df[ind],
                    mode='lines', name=ind.upper(),
                    line=dict(color=colors.get(ind, '#888888'), width=1.5)
                ), row=1, col=1)

        # Bollinger Bands
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            fig.add_trace(go.Scatter(
                x=x_vals, y=df['bb_upper'],
                mode='lines', name='BB Upper',
                line=dict(color='rgba(255,255,255,0.3)', width=1),
                showlegend=False
            ), row=1, col=1)
            fig.add_trace(go.Scatter(
                x=x_vals, y=df['bb_lower'],
                mode='lines', name='BB Lower',
                line=dict(color='rgba(255,255,255,0.3)', width=1),
                fill='tonexty', fillcolor='rgba(100,100,255,0.1)',
                showlegend=False
            ), row=1, col=1)

        # Support/Resistance lines
        if 'nearest_support' in df.columns:
            last_support = df['nearest_support'].iloc[-1]
            last_resistance = df['nearest_resistance'].iloc[-1]
            fig.add_hline(y=last_support, line_dash="dash", line_color="#00ff88",
                          annotation_text=f"Support: {last_support:.2f}", row=1, col=1)
            fig.add_hline(y=last_resistance, line_dash="dash", line_color="#ff4444",
                          annotation_text=f"Resistance: {last_resistance:.2f}", row=1, col=1)

        # RSI
        if 'rsi' in df.columns:
            fig.add_trace(go.Scatter(
                x=x_vals, y=df['rsi'],
                mode='lines', name='RSI',
                line=dict(color='#00aaff', width=1.5)
            ), row=2, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ff4444",
                          annotation_text="OB", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#00ff88",
                          annotation_text="OS", row=2, col=1)
            fig.add_hline(y=50, line_dash="dot", line_color="#888888", row=2, col=1)
            fig.update_yaxes(range=[0, 100], row=2, col=1)

        # Volume
        if show_volume and 'volume' in df.columns:
            colors_vol = ['#00ff88' if df['close'].iloc[i] >= df['open'].iloc[i]
                          else '#ff4444' for i in range(len(df))]
            fig.add_trace(go.Bar(
                x=x_vals, y=df['volume'],
                name='Volume', marker_color=colors_vol, opacity=0.6
            ), row=3, col=1)

            if 'volume_sma' in df.columns:
                fig.add_trace(go.Scatter(
                    x=x_vals, y=df['volume_sma'],
                    mode='lines', name='Vol MA',
                    line=dict(color='#ffaa00', width=1.5)
                ), row=3, col=1)

        fig.update_layout(
            title=f'{symbol} - Advanced Technical Analysis',
            template='plotly_dark', height=900,
            xaxis_rangeslider_visible=False,
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
        )

        return fig

    def create_rsi_chart(self, df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()
        x_vals = df['date'] if 'date' in df.columns else df.index

        if 'rsi' in df.columns:
            fig.add_trace(go.Scatter(x=x_vals, y=df['rsi'], mode='lines',
                                     name='RSI', line=dict(color='#00aaff', width=2)))
            fig.add_hline(y=70, line_dash="dash", line_color="#ff4444", annotation_text="Overbought")
            fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", annotation_text="Oversold")
            fig.add_hline(y=50, line_dash="dot", line_color="#888888")
            fig.update_yaxes(range=[0, 100])

        fig.update_layout(title='RSI (14)', template='plotly_dark', height=400)
        return fig

    def create_adx_chart(self, df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()
        x_vals = df['date'] if 'date' in df.columns else df.index

        if 'adx' in df.columns:
            fig.add_trace(go.Scatter(x=x_vals, y=df['adx'], mode='lines',
                                     name='ADX', line=dict(color='#ffaa00', width=2)))
            fig.add_trace(go.Scatter(x=x_vals, y=df['plus_di'], mode='lines',
                                     name='+DI', line=dict(color='#00ff88', width=1)))
            fig.add_trace(go.Scatter(x=x_vals, y=df['minus_di'], mode='lines',
                                     name='-DI', line=dict(color='#ff4444', width=1)))
            fig.add_hline(y=25, line_dash="dash", line_color="#ffffff", annotation_text="Trend Threshold")

        fig.update_layout(title='ADX & Directional Movement', template='plotly_dark', height=400)
        return fig

    def create_stochastic_chart(self, df: pd.DataFrame) -> go.Figure:
        fig = go.Figure()
        x_vals = df['date'] if 'date' in df.columns else df.index

        if 'stochastic_k' in df.columns:
            fig.add_trace(go.Scatter(x=x_vals, y=df['stochastic_k'], mode='lines',
                                     name='%K', line=dict(color='#00aaff', width=2)))
            fig.add_trace(go.Scatter(x=x_vals, y=df['stochastic_d'], mode='lines',
                                     name='%D', line=dict(color='#ffaa00', width=2)))
            fig.add_hline(y=80, line_dash="dash", line_color="#ff4444")
            fig.add_hline(y=20, line_dash="dash", line_color="#00ff88")
            fig.update_yaxes(range=[0, 100])

        fig.update_layout(title='Stochastic Oscillator', template='plotly_dark', height=400)
        return fig

    def create_macd_chart(self, df: pd.DataFrame) -> go.Figure:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            vertical_spacing=0.1, row_heights=[0.7, 0.3])
        x_vals = df['date'] if 'date' in df.columns else df.index

        if 'macd' in df.columns:
            fig.add_trace(go.Scatter(x=x_vals, y=df['macd'], mode='lines',
                                     name='MACD', line=dict(color='#00aaff', width=2)), row=1, col=1)
            fig.add_trace(go.Scatter(x=x_vals, y=df['macd_signal'], mode='lines',
                                     name='Signal', line=dict(color='#ffaa00', width=2)), row=1, col=1)

            colors = ['#00ff88' if df['macd_hist'].iloc[i] >= 0 else '#ff4444' for i in range(len(df))]
            fig.add_trace(go.Bar(x=x_vals, y=df['macd_hist'], name='Histogram',
                                 marker_color=colors), row=2, col=1)

        fig.update_layout(title='MACD', template='plotly_dark', height=500)
        return fig

    def create_ichimoku_chart(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        fig = go.Figure()
        x_vals = df['date'] if 'date' in df.columns else df.index

        fig.add_trace(go.Candlestick(x=x_vals, open=df['open'], high=df['high'],
                                     low=df['low'], close=df['close'], name='Price'))

        if 'tenkan_sen' in df.columns:
            fig.add_trace(go.Scatter(x=x_vals, y=df['tenkan_sen'], mode='lines',
                                     name='Tenkan-sen', line=dict(color='#ff4444', width=1.5)))
            fig.add_trace(go.Scatter(x=x_vals, y=df['kijun_sen'], mode='lines',
                                     name='Kijun-sen', line=dict(color='#00aaff', width=1.5)))
            fig.add_trace(go.Scatter(x=x_vals, y=df['senkou_span_a'], mode='lines',
                                     name='Senkou A', line=dict(color='#00ff88', width=1),
                                     fill='tonexty', fillcolor='rgba(0,255,136,0.1)'))
            fig.add_trace(go.Scatter(x=x_vals, y=df['senkou_span_b'], mode='lines',
                                     name='Senkou B', line=dict(color='#ff4444', width=1),
                                     fill='tonexty', fillcolor='rgba(255,68,68,0.1)'))

        fig.update_layout(title=f'{symbol} - Ichimoku Cloud',
                          template='plotly_dark', height=700,
                          xaxis_rangeslider_visible=False)
        return fig

    def create_equity_curve(self, equity_data: list) -> go.Figure:
        fig = go.Figure()
        df = pd.DataFrame(equity_data)

        if not df.empty:
            fig.add_trace(go.Scatter(x=df['date'], y=df['equity'], mode='lines',
                                     name='Equity', line=dict(color='#00aaff', width=2),
                                     fill='tozeroy', fillcolor='rgba(0,170,255,0.1)'))

            initial = df['equity'].iloc[0]
            fig.add_hline(y=initial, line_dash="dash", line_color="#888888",
                          annotation_text="Initial Capital")

            # Add drawdown shading
            if 'drawdown' in df.columns:
                fig.add_trace(go.Scatter(x=df['date'], y=df['equity'] * (1 + df['drawdown']/100),
                                         mode='lines', name='Drawdown',
                                         line=dict(color='rgba(255,0,0,0.3)', width=0),
                                         fill='tonexty', fillcolor='rgba(255,0,0,0.1)'))

        fig.update_layout(title='Equity Curve & Drawdown', template='plotly_dark', height=500)
        return fig

    def create_drawdown_chart(self, equity_data: list) -> go.Figure:
        fig = go.Figure()
        df = pd.DataFrame(equity_data)

        if 'drawdown' in df.columns:
            fig.add_trace(go.Scatter(x=df['date'], y=df['drawdown'], mode='lines',
                                     name='Drawdown %', line=dict(color='#ff4444', width=2),
                                     fill='tozeroy', fillcolor='rgba(255,68,68,0.2)'))
            fig.add_hline(y=0, line_dash="solid", line_color="#888888")

        fig.update_layout(title='Drawdown Analysis', template='plotly_dark', height=400)
        return fig

    def create_comparison_chart(self, data_dict: dict, normalize: bool = True) -> go.Figure:
        fig = go.Figure()
        colors = ['#00aaff', '#ff4444', '#00ff88', '#ffaa00', '#ff00ff', '#00ffff',
                  '#ff6600', '#66ff00', '#ff69b4', '#00ffcc']

        for i, (symbol, df) in enumerate(data_dict.items()):
            if df is not None and not df.empty:
                y_vals = (df['close'] / df['close'].iloc[0]) * 100 if normalize else df['close']
                x_vals = df['date'] if 'date' in df.columns else df.index

                fig.add_trace(go.Scatter(x=x_vals, y=y_vals, mode='lines',
                                         name=symbol, line=dict(color=colors[i % len(colors)], width=2)))

        title = 'Normalized Price Comparison (Base = 100)' if normalize else 'Price Comparison'
        fig.update_layout(title=title, template='plotly_dark', height=500)
        return fig

    def create_sector_heatmap(self, sector_data: Dict[str, float]) -> go.Figure:
        sectors = list(sector_data.keys())
        values = list(sector_data.values())
        colors = ['#4caf50' if v > 0 else '#f44336' for v in values]

        fig = go.Figure(go.Bar(
            x=sectors, y=values,
            marker_color=colors,
            text=[f"{v:+.2f}%" for v in values],
            textposition='outside'
        ))

        fig.update_layout(title='Sector Performance', template='plotly_dark',
                          height=400, showlegend=False)
        return fig

    def create_correlation_heatmap(self, corr_matrix: pd.DataFrame) -> go.Figure:
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu',
            zmin=-1, zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate='%{text}',
            textfont={"size": 10}
        ))

        fig.update_layout(title='Correlation Matrix', template='plotly_dark', height=600)
        return fig

    def create_monte_carlo_chart(self, mc_results: Dict) -> go.Figure:
        fig = go.Figure()

        percentiles = ['5%', '25%', 'Median', '75%', '95%']
        prices = [mc_results['percentile_5'], mc_results['percentile_25'],
                  mc_results['median_price'], mc_results['percentile_75'],
                  mc_results['percentile_95']]
        colors = ['#ff4444', '#ffaa00', '#00ff88', '#00aaff', '#aa00ff']

        for p, price, color in zip(percentiles, prices, colors):
            fig.add_trace(go.Bar(x=[p], y=[price], name=p, marker_color=color))

        fig.add_hline(y=mc_results['mean_price'], line_dash="dash", line_color="#ffffff",
                      annotation_text=f"Mean: {mc_results['mean_price']:.2f}")

        fig.update_layout(title='Monte Carlo Simulation - Price Distribution',
                          template='plotly_dark', height=400, showlegend=False)
        return fig

    def create_multi_indicator_chart(self, df: pd.DataFrame, symbol: str) -> go.Figure:
        fig = make_subplots(rows=4, cols=1, shared_xaxes=True,
                            vertical_spacing=0.05,
                            row_heights=[0.4, 0.2, 0.2, 0.2],
                            subplot_titles=(f'{symbol} Price', 'MACD', 'RSI', 'Volume'))

        x_vals = df['date'] if 'date' in df.columns else df.index

        # Price
        fig.add_trace(go.Candlestick(x=x_vals, open=df['open'], high=df['high'],
                                     low=df['low'], close=df['close'], name='Price'), row=1, col=1)

        # MACD
        if 'macd' in df.columns:
            fig.add_trace(go.Scatter(x=x_vals, y=df['macd'], mode='lines',
                                     name='MACD', line=dict(color='#00aaff')), row=2, col=1)
            fig.add_trace(go.Scatter(x=x_vals, y=df['macd_signal'], mode='lines',
                                     name='Signal', line=dict(color='#ffaa00')), row=2, col=1)

        # RSI
        if 'rsi' in df.columns:
            fig.add_trace(go.Scatter(x=x_vals, y=df['rsi'], mode='lines',
                                     name='RSI', line=dict(color='#00ff88')), row=3, col=1)
            fig.add_hline(y=70, line_dash="dash", line_color="#ff4444", row=3, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="#00ff88", row=3, col=1)

        # Volume
        if 'volume' in df.columns:
            colors = ['#00ff88' if df['close'].iloc[i] >= df['open'].iloc[i]
                      else '#ff4444' for i in range(len(df))]
            fig.add_trace(go.Bar(x=x_vals, y=df['volume'], name='Volume',
                                 marker_color=colors, opacity=0.6), row=4, col=1)

        fig.update_layout(title=f'{symbol} - Multi-Indicator Dashboard',
                          template='plotly_dark', height=1000,
                          xaxis_rangeslider_visible=False)
        return fig

chart_engine = ChartEngine()

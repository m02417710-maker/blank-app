"""
EGX Pro Ultimate v30 — ML Engine + Backtest
✅ Walk-Forward Validation (بدون data leakage)
✅ 10 استراتيجيات باكتست مع عمولات EGX الحقيقية
✅ Kelly Criterion + Sharpe + Calmar + Max Drawdown
"""

import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

EGX_COMMISSION   = 0.00135
EGX_STAMP        = 0.001
EGX_CUSTODY      = 0.0003
EGX_TOTAL_COST   = EGX_COMMISSION + EGX_STAMP + EGX_CUSTODY
EGX_SLIPPAGE     = 0.002
PRICE_LIMIT      = 0.10
MIN_TRADE_EGP    = 500

# ═══════════════════════════════════════════════════════════════
# نموذج ML مع Walk-Forward Validation صحيح
# ═══════════════════════════════════════════════════════════════
class EGXMLPredictor:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols: List[str] = []
        self.is_trained = False
        self.metrics: Dict = {}
        self.wf_results: List[Dict] = []

    def _build_features(self, df: pd.DataFrame) -> pd.DataFrame:
        feat = pd.DataFrame(index=df.index)
        c = df['close']
        feat['returns_1d']  = c.pct_change().shift(1)
        feat['returns_3d']  = c.pct_change(3).shift(1)
        feat['returns_5d']  = c.pct_change(5).shift(1)
        feat['returns_10d'] = c.pct_change(10).shift(1)
        feat['returns_20d'] = c.pct_change(20).shift(1)
        for col in ['rsi','macd','macd_signal','macd_hist','adx',
                    'stoch_k','stoch_d','cci','williams_r','roc',
                    'momentum','supertrend_dir','di_plus','di_minus']:
            if col in df.columns:
                feat[col] = df[col].shift(1)
        if 'ema_20' in df.columns and 'ema_50' in df.columns:
            feat['ema_cross'] = (df['ema_20']/df['ema_50'].replace(0,np.nan)-1).shift(1)
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            bb_range = (df['bb_upper']-df['bb_lower']).replace(0,np.nan)
            feat['bb_pos']   = ((c-df['bb_lower'])/bb_range).shift(1)
            feat['bb_width'] = (bb_range/c).shift(1)
        if 'vwap' in df.columns:
            feat['price_vs_vwap'] = (c/df['vwap'].replace(0,np.nan)-1).shift(1)
        if 'vol_ratio' in df.columns:
            feat['vol_ratio'] = df['vol_ratio'].shift(1)
        if 'atr' in df.columns:
            feat['atr_pct'] = (df['atr']/c.replace(0,np.nan)).shift(1)
        if 'volatility_20d' in df.columns:
            feat['volatility'] = df['volatility_20d'].shift(1)
        forward_5d = c.pct_change(5).shift(-5)
        feat['target'] = (forward_5d > 0.02).astype(int)
        return feat.dropna()

    def train_walk_forward(self, df: pd.DataFrame, n_splits: int = 5) -> Dict:
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.preprocessing import RobustScaler
            from sklearn.model_selection import TimeSeriesSplit
            from sklearn.metrics import accuracy_score, roc_auc_score, precision_score
        except ImportError:
            return {'error': 'scikit-learn غير مثبت'}

        feat = self._build_features(df)
        if len(feat) < 100:
            return {'error': 'بيانات غير كافية (أقل من 100 يوم)'}

        X = feat.drop('target', axis=1).values
        y = feat['target'].values
        tscv = TimeSeriesSplit(n_splits=n_splits, gap=5)
        fold_metrics = []
        self.wf_results = []

        for fold_idx, (train_idx, test_idx) in enumerate(tscv.split(X)):
            if len(train_idx) < 50 or len(test_idx) < 10:
                continue
            X_train, X_test = X[train_idx], X[test_idx]
            y_train, y_test = y[train_idx], y[test_idx]
            scaler = RobustScaler()
            X_tr = scaler.fit_transform(X_train)
            X_te = scaler.transform(X_test)
            model = GradientBoostingClassifier(n_estimators=100, learning_rate=0.05,
                                               max_depth=3, subsample=0.8,
                                               min_samples_leaf=10, random_state=42)
            model.fit(X_tr, y_train)
            preds = model.predict(X_te)
            proba = model.predict_proba(X_te)[:,1]
            acc  = accuracy_score(y_test, preds)
            try: auc = roc_auc_score(y_test, proba)
            except: auc = 0.5
            prec = precision_score(y_test, preds, zero_division=0)
            fold_metrics.append({'acc':acc,'auc':auc,'prec':prec})
            self.wf_results.append({'fold':fold_idx+1,'train_size':len(train_idx),
                'test_size':len(test_idx),'accuracy':f"{acc*100:.1f}%",
                'auc':f"{auc:.3f}",'precision':f"{prec*100:.1f}%"})

        if not fold_metrics:
            return {'error': 'فشل التدريب'}

        self.scaler = RobustScaler()
        X_all = self.scaler.fit_transform(X)
        self.model = GradientBoostingClassifier(n_estimators=150, learning_rate=0.05,
                                                max_depth=3, subsample=0.8,
                                                min_samples_leaf=10, random_state=42)
        self.model.fit(X_all, y)
        self.feature_cols = feat.drop('target', axis=1).columns.tolist()
        self.is_trained = True
        avg_acc  = np.mean([f['acc']  for f in fold_metrics])
        avg_auc  = np.mean([f['auc']  for f in fold_metrics])
        avg_prec = np.mean([f['prec'] for f in fold_metrics])
        self.metrics = {'avg_accuracy':avg_acc,'avg_auc':avg_auc,
                        'avg_precision':avg_prec,'n_folds':len(fold_metrics),
                        'n_features':len(self.feature_cols),
                        'training_samples':len(X),'folds':self.wf_results}
        return self.metrics

    def predict(self, df: pd.DataFrame) -> Tuple[str, float, str]:
        if not self.is_trained or self.model is None:
            return "غير متاح", 0.0, "⚪"
        try:
            feat = self._build_features(df)
            if feat.empty:
                return "بيانات غير كافية", 0.0, "⚪"
            last_feat = feat.drop('target', axis=1).iloc[-1:].values
            last_s = self.scaler.transform(last_feat)
            proba = self.model.predict_proba(last_s)[0][1]
            if proba >= 0.70:   return "شراء قوي (ML)",   proba, "🟢"
            elif proba >= 0.55: return "ميل للشراء (ML)", proba, "🟩"
            elif proba <= 0.30: return "بيع قوي (ML)",    proba, "🔴"
            elif proba <= 0.45: return "ميل للبيع (ML)",  proba, "🟥"
            else:               return "محايد (ML)",       proba, "⚪"
        except Exception as e:
            return "خطأ", 0.0, "⚪"

    def get_feature_importance(self) -> pd.DataFrame:
        if not self.is_trained or not hasattr(self.model,'feature_importances_'):
            return pd.DataFrame()
        return pd.DataFrame({'feature':self.feature_cols,
                             'importance':self.model.feature_importances_})\
                 .sort_values('importance',ascending=False).head(15)


# ═══════════════════════════════════════════════════════════════
# Backtest Engine
# ═══════════════════════════════════════════════════════════════
@dataclass
class Trade:
    entry_date: Any; exit_date: Any
    entry_price: float; exit_price: float
    shares: int; capital_used: float
    pnl: float; pnl_pct: float; trade_cost: float; strategy: str

@dataclass
class BacktestResult:
    strategy: str
    trades: List[Trade]          = field(default_factory=list)
    equity_curve: pd.Series      = field(default_factory=pd.Series)
    total_return: float = 0.0;   annualized_return: float = 0.0
    sharpe_ratio: float = 0.0;   calmar_ratio: float = 0.0
    max_drawdown: float = 0.0;   win_rate: float = 0.0
    profit_factor: float = 0.0;  avg_win: float = 0.0
    avg_loss: float = 0.0;       total_trades: int = 0
    kelly_pct: float = 0.0;      risk_reward: float = 0.0

def _apply_costs(price: float, direction: str = 'buy') -> float:
    cost = price * (EGX_TOTAL_COST + EGX_SLIPPAGE)
    return price + cost if direction == 'buy' else price - cost

def _calc_equity_metrics(equity: pd.Series, trades: List[Trade], rf: float = 0.17) -> Dict:
    if len(equity) < 2: return {}
    rets = equity.pct_change().dropna()
    total_ret = equity.iloc[-1]/equity.iloc[0] - 1
    n_years = len(equity)/252
    ann_ret = (1+total_ret)**(1/max(n_years,0.1)) - 1
    excess  = rets - rf/252
    sharpe  = excess.mean()/excess.std()*np.sqrt(252) if excess.std()>0 else 0
    roll_max = equity.cummax()
    max_dd   = ((equity - roll_max)/roll_max).min()
    calmar   = ann_ret/abs(max_dd) if abs(max_dd)>0.001 else 0
    wins  = [t for t in trades if t.pnl>0]
    loses = [t for t in trades if t.pnl<=0]
    wr    = len(wins)/len(trades) if trades else 0
    avg_w = np.mean([t.pnl_pct for t in wins])  if wins  else 0
    avg_l = abs(np.mean([t.pnl_pct for t in loses])) if loses else 0.001
    pf    = (sum(t.pnl for t in wins)/abs(sum(t.pnl for t in loses))
             if loses and sum(t.pnl for t in loses)!=0 else 999)
    rr    = avg_w/avg_l if avg_l>0 else 0
    kelly = max(0, min(wr-(1-wr)/rr if rr>0 else 0, 0.25))
    return dict(total_return=total_ret, annualized_return=ann_ret,
                sharpe_ratio=sharpe, calmar_ratio=calmar, max_drawdown=max_dd,
                win_rate=wr, profit_factor=pf, avg_win=avg_w, avg_loss=avg_l,
                kelly_pct=kelly, risk_reward=rr)

def _run_single_backtest(df: pd.DataFrame, strategy: str,
                          initial_capital: float = 100_000) -> BacktestResult:
    result = BacktestResult(strategy=strategy)
    if df is None or len(df) < 60: return result
    capital = initial_capital
    equity_vals, eq_dates, trades = [capital], [df.index[0]], []
    position = 0; entry_price = 0.0; entry_date = None
    c = df['close']

    def g(col, i, d=0):
        try: return float(df[col].iloc[i]) if col in df.columns else d
        except: return d

    for i in range(1, len(df)-1):
        price = float(c.iloc[i])
        if price <= 0: continue
        buy_sig = sell_sig = False

        if strategy == 'EMA Cross':
            e9,e20,pe9,pe20 = g('ema_9',i),g('ema_20',i),g('ema_9',i-1),g('ema_20',i-1)
            buy_sig = pe9<pe20 and e9>e20; sell_sig = pe9>pe20 and e9<e20

        elif strategy == 'RSI Reversal':
            r,pr = g('rsi',i),g('rsi',i-1)
            buy_sig = pr<30 and r>=30; sell_sig = pr>70 and r<=70

        elif strategy == 'MACD Cross':
            m,s,pm,ps = g('macd',i),g('macd_signal',i),g('macd',i-1),g('macd_signal',i-1)
            buy_sig = pm<ps and m>s; sell_sig = pm>ps and m<s

        elif strategy == 'Bollinger Breakout':
            pc,bu,bl = float(c.iloc[i-1]),g('bb_upper',i),g('bb_lower',i)
            buy_sig = pc<=bl and price>bl; sell_sig = pc>=bu and price<bu

        elif strategy == 'Supertrend':
            sd,psd = g('supertrend_dir',i),g('supertrend_dir',i-1)
            buy_sig = psd<=0 and sd==1; sell_sig = psd>=0 and sd==-1

        elif strategy == 'VWAP + RSI':
            r,vw = g('rsi',i),g('vwap',i)
            buy_sig = price>vw and r<45; sell_sig = price<vw and r>55

        elif strategy == 'Parabolic SAR':
            ps,pps,pc = g('psar',i),g('psar',i-1),float(c.iloc[i-1])
            buy_sig = pc<pps and price>ps; sell_sig = pc>pps and price<ps

        elif strategy == 'Ichimoku':
            tk,kj,sa,sb = g('ich_tenkan',i),g('ich_kijun',i),g('ich_senkou_a',i),g('ich_senkou_b',i)
            ct,cb = max(sa,sb),min(sa,sb)
            buy_sig = price>ct and tk>kj; sell_sig = price<cb and tk<kj

        elif strategy == 'ADX Trend':
            adx,dip,dim = g('adx',i),g('di_plus',i),g('di_minus',i)
            buy_sig  = adx>25 and dip>dim and g('di_plus',i-1)<=g('di_minus',i-1)
            sell_sig = adx>25 and dim>dip and g('di_minus',i-1)<=g('di_plus',i-1)

        elif strategy == 'Multi-Signal':
            sc = 0
            rsi_v = g('rsi',i)
            if rsi_v<40: sc+=1
            elif rsi_v>60: sc-=1
            if g('macd',i)>g('macd_signal',i): sc+=1
            else: sc-=1
            if price>g('ema_50',i): sc+=1
            else: sc-=1
            if g('supertrend_dir',i)==1: sc+=1
            else: sc-=1
            if price>g('vwap',i): sc+=1
            else: sc-=1
            buy_sig = sc>=3; sell_sig = sc<=-3

        if buy_sig and position==0 and capital>MIN_TRADE_EGP:
            cp = _apply_costs(price,'buy')
            shares = int((capital*0.95)/cp)
            if shares>0:
                tc = shares*cp*EGX_TOTAL_COST
                capital -= shares*cp+tc
                position, entry_price, entry_date = shares, cp, df.index[i]

        elif sell_sig and position>0:
            sp = _apply_costs(price,'sell')
            proc = position*sp
            tc   = proc*EGX_TOTAL_COST
            pnl  = proc-tc-position*entry_price
            pnl_pct = pnl/(position*entry_price) if entry_price>0 else 0
            capital += proc-tc
            trades.append(Trade(entry_date=entry_date, exit_date=df.index[i],
                entry_price=entry_price, exit_price=sp, shares=position,
                capital_used=position*entry_price, pnl=pnl, pnl_pct=pnl_pct,
                trade_cost=tc, strategy=strategy))
            position = 0

        equity_vals.append(capital + (position*price if position>0 else 0))
        eq_dates.append(df.index[i])

    if position>0:
        lp = float(c.iloc[-1]); sp = _apply_costs(lp,'sell')
        proc = position*sp; tc = proc*EGX_TOTAL_COST
        pnl  = proc-tc-position*entry_price
        pnl_pct = pnl/(position*entry_price) if entry_price>0 else 0
        capital += proc-tc
        trades.append(Trade(entry_date=entry_date, exit_date=df.index[-1],
            entry_price=entry_price, exit_price=sp, shares=position,
            capital_used=position*entry_price, pnl=pnl, pnl_pct=pnl_pct,
            trade_cost=tc, strategy=strategy))

    equity = pd.Series(equity_vals, index=eq_dates[:len(equity_vals)])
    m = _calc_equity_metrics(equity, trades)
    result.trades=trades; result.equity_curve=equity; result.total_trades=len(trades)
    result.total_return=m.get('total_return',0); result.annualized_return=m.get('annualized_return',0)
    result.sharpe_ratio=m.get('sharpe_ratio',0); result.calmar_ratio=m.get('calmar_ratio',0)
    result.max_drawdown=m.get('max_drawdown',0); result.win_rate=m.get('win_rate',0)
    result.profit_factor=m.get('profit_factor',0); result.avg_win=m.get('avg_win',0)
    result.avg_loss=m.get('avg_loss',0); result.kelly_pct=m.get('kelly_pct',0)
    result.risk_reward=m.get('risk_reward',0)
    return result

ALL_STRATEGIES = ['EMA Cross','RSI Reversal','MACD Cross','Bollinger Breakout',
                  'Supertrend','VWAP + RSI','Parabolic SAR','Ichimoku',
                  'ADX Trend','Multi-Signal']

def run_all_backtests(df, initial_capital=100_000, strategies=None):
    strats = strategies or ALL_STRATEGIES
    return [_run_single_backtest(df, s, initial_capital) for s in strats]

def backtest_summary_df(results: List[BacktestResult]) -> pd.DataFrame:
    rows = []
    for r in results:
        rows.append({'الاستراتيجية':r.strategy,'العائد الكلي':f"{r.total_return*100:.1f}%",
            'العائد السنوي':f"{r.annualized_return*100:.1f}%",'Sharpe':f"{r.sharpe_ratio:.2f}",
            'Calmar':f"{r.calmar_ratio:.2f}",'Max DD':f"{r.max_drawdown*100:.1f}%",
            'نسبة الربح':f"{r.win_rate*100:.1f}%",'معامل الربح':f"{r.profit_factor:.2f}",
            'عدد الصفقات':r.total_trades,'Kelly %':f"{r.kelly_pct*100:.1f}%",
            'R:R':f"{r.risk_reward:.2f}"})
    return pd.DataFrame(rows)

class PortfolioManager:
    def __init__(self, capital=100_000):
        self.capital = capital

    def calc_position_size(self, price, win_rate, avg_win, avg_loss, max_risk_pct=0.02):
        if avg_loss<=0: return {'shares':0,'capital':0,'kelly':0}
        rr = avg_win/avg_loss if avg_loss>0 else 1
        kelly = max(0, min(win_rate-(1-win_rate)/rr if rr>0 else 0, 0.15))*0.5
        risk_based  = (self.capital*max_risk_pct)/(price*avg_loss) if price>0 else 0
        kelly_based = (self.capital*kelly)/price if price>0 else 0
        shares = int(min(risk_based, kelly_based))
        return {'shares':shares,'capital':shares*price,'kelly':kelly,
                'position_pct':(shares*price)/self.capital*100 if self.capital>0 else 0}

    def calc_stop_loss(self, entry, atr, multiplier=2.0):
        stop = entry - multiplier*atr
        take = entry + multiplier*2*atr
        return {'stop_loss':stop,'take_profit':take,
                'risk_pct':(entry-stop)/entry*100,
                'reward_pct':(take-entry)/entry*100,
                'rr_ratio':(take-entry)/(entry-stop) if entry>stop else 0}

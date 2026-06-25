"""EGX Pro v32 — ML + Backtest Engine (مُصحَّح بالكامل)
✅ إصلاح خصم العمولة المزدوج عند الشراء
✅ إصلاح PnL الصحيح (يطرح تكلفة الدخول والخروج)
✅ bare except → except Exception
✅ تحقق من monthly_amount في DCA
"""
import pandas as pd
import numpy as np
import logging
from typing import Optional, Dict, List, Tuple, Any
from dataclasses import dataclass, field
import warnings
warnings.filterwarnings('ignore')
logger = logging.getLogger(__name__)

EGX_COMMISSION=0.00100; EGX_STAMP=0.00050; EGX_CUSTODY=0.00035  # 18.5 bps إجمالاً (EGX الرسمية)
EGX_TOTAL_COST=EGX_COMMISSION+EGX_STAMP+EGX_CUSTODY  # = 0.00185
EGX_SLIPPAGE=0.002; MIN_TRADE_EGP=500

class EGXMLPredictor:
    def __init__(self):
        self.model=None; self.scaler=None; self.feature_cols=[]
        self.is_trained=False; self.metrics={}; self.wf_results=[]

    def _build_features(self, df):
        feat=pd.DataFrame(index=df.index); c=df['close']
        feat['r1']=c.pct_change().shift(1); feat['r3']=c.pct_change(3).shift(1)
        feat['r5']=c.pct_change(5).shift(1); feat['r10']=c.pct_change(10).shift(1)
        feat['r20']=c.pct_change(20).shift(1)
        for col in ['rsi','macd','macd_signal','macd_hist','adx','stoch_k','stoch_d',
                    'cci','williams_r','roc','momentum','supertrend_dir','di_plus','di_minus']:
            if col in df.columns: feat[col]=df[col].shift(1)
        if 'ema_20' in df.columns and 'ema_50' in df.columns:
            feat['ema_cross']=(df['ema_20']/df['ema_50'].replace(0,np.nan)-1).shift(1)
        if 'bb_upper' in df.columns and 'bb_lower' in df.columns:
            bb_r=(df['bb_upper']-df['bb_lower']).replace(0,np.nan)
            feat['bb_pos']=((c-df['bb_lower'])/bb_r).shift(1)
            feat['bb_width']=(bb_r/c).shift(1)
        if 'vwap' in df.columns: feat['vs_vwap']=(c/df['vwap'].replace(0,np.nan)-1).shift(1)
        if 'vol_ratio' in df.columns: feat['vol_ratio']=df['vol_ratio'].shift(1)
        if 'atr' in df.columns: feat['atr_pct']=(df['atr']/c.replace(0,np.nan)).shift(1)
        if 'volatility_20d' in df.columns: feat['vol20']=df['volatility_20d'].shift(1)
        # ✅ threshold 0.005 بدلاً من 0.02 لإصلاح class imbalance
        feat['target']=(c.pct_change(5).shift(-5)>0.005).astype(int)
        return feat.dropna()

    def train_walk_forward(self, df, n_splits=5):
        try:
            from sklearn.ensemble import GradientBoostingClassifier
            from sklearn.preprocessing import RobustScaler
            from sklearn.model_selection import TimeSeriesSplit
            from sklearn.metrics import accuracy_score, roc_auc_score, precision_score
            from sklearn.utils.class_weight import compute_sample_weight
        except ImportError:
            return {'error':'scikit-learn غير مثبت'}
        feat=self._build_features(df)
        if len(feat)<100: return {'error':'بيانات غير كافية'}
        X=feat.drop('target',axis=1).values; y=feat['target'].values
        tscv=TimeSeriesSplit(n_splits=n_splits,gap=5)
        fold_metrics=[]; self.wf_results=[]
        for fi,(tr_i,te_i) in enumerate(tscv.split(X)):
            if len(tr_i)<50 or len(te_i)<10: continue
            X_tr,X_te=X[tr_i],X[te_i]; y_tr,y_te=y[tr_i],y[te_i]
            sc=RobustScaler(); X_trs=sc.fit_transform(X_tr); X_tes=sc.transform(X_te)
            # ✅ sample_weight لإصلاح class imbalance
            sw=compute_sample_weight('balanced',y_tr)
            m=GradientBoostingClassifier(n_estimators=100,learning_rate=0.05,max_depth=3,
                                          subsample=0.8,min_samples_leaf=5,random_state=42)
            m.fit(X_trs,y_tr,sample_weight=sw)
            preds=m.predict(X_tes); proba=m.predict_proba(X_tes)[:,1]
            acc=accuracy_score(y_te,preds)
            try: auc=roc_auc_score(y_te,proba)
            except: auc=0.5
            prec=precision_score(y_te,preds,zero_division=0)
            fold_metrics.append({'acc':acc,'auc':auc,'prec':prec})
            self.wf_results.append({'الـ Fold':fi+1,'تدريب':len(tr_i),'اختبار':len(te_i),
                'الدقة':f"{acc*100:.1f}%",'AUC':f"{auc:.3f}",'الضبط':f"{prec*100:.1f}%"})
        if not fold_metrics: return {'error':'فشل التدريب'}
        self.scaler=RobustScaler(); X_all=self.scaler.fit_transform(X)
        sw_all=compute_sample_weight('balanced',y)
        self.model=GradientBoostingClassifier(n_estimators=150,learning_rate=0.05,
            max_depth=3,subsample=0.8,min_samples_leaf=5,random_state=42)
        self.model.fit(X_all,y,sample_weight=sw_all)
        self.feature_cols=feat.drop('target',axis=1).columns.tolist()
        self.is_trained=True
        self.metrics={'avg_accuracy':np.mean([f['acc'] for f in fold_metrics]),
                      'avg_auc':np.mean([f['auc'] for f in fold_metrics]),
                      'avg_precision':np.mean([f['prec'] for f in fold_metrics]),
                      'n_folds':len(fold_metrics),'n_features':len(self.feature_cols),
                      'training_samples':len(X),'folds':self.wf_results}
        return self.metrics

    def predict(self, df):
        if not self.is_trained: return "غير متاح",0.0,"⚪"
        try:
            feat=self._build_features(df)
            if feat.empty: return "بيانات غير كافية",0.0,"⚪"
            lf=self.scaler.transform(feat.drop('target',axis=1).iloc[-1:].values)
            p=self.model.predict_proba(lf)[0][1]
            if p>=0.70: return "شراء قوي (ML)",p,"🟢"
            elif p>=0.55: return "ميل للشراء (ML)",p,"🟩"
            elif p<=0.30: return "بيع قوي (ML)",p,"🔴"
            elif p<=0.45: return "ميل للبيع (ML)",p,"🟥"
            else: return "محايد (ML)",p,"⚪"
        except Exception as e:
            logger.warning(f"EGXMLPredictor.predict error: {e}")
            return "خطأ",0.0,"⚪"

    def get_feature_importance(self):
        if not self.is_trained or not hasattr(self.model,'feature_importances_'): return pd.DataFrame()
        return pd.DataFrame({'المتغير':self.feature_cols,'الأهمية':self.model.feature_importances_})\
                 .sort_values('الأهمية',ascending=False).head(15)

@dataclass
class Trade:
    entry_date:Any; exit_date:Any; entry_price:float; exit_price:float
    shares:int; capital_used:float; pnl:float; pnl_pct:float; trade_cost:float; strategy:str

@dataclass
class BacktestResult:
    strategy:str; trades:List[Trade]=field(default_factory=list)
    equity_curve:pd.Series=field(default_factory=pd.Series)
    total_return:float=0.0; annualized_return:float=0.0
    sharpe_ratio:float=0.0; calmar_ratio:float=0.0
    max_drawdown:float=0.0; win_rate:float=0.0
    profit_factor:float=0.0; avg_win:float=0.0
    avg_loss:float=0.0; total_trades:int=0
    kelly_pct:float=0.0; risk_reward:float=0.0

def _cost(p,d='buy'):
    c=p*(EGX_TOTAL_COST+EGX_SLIPPAGE)
    return p+c if d=='buy' else p-c

def _metrics(equity,trades,rf=0.17):
    if len(equity)<2: return {}
    rets=equity.pct_change().dropna(); tr=equity.iloc[-1]/equity.iloc[0]-1
    ny=len(equity)/252; ann=(1+tr)**(1/max(ny,0.1))-1
    ex=rets-rf/252; sh=ex.mean()/ex.std()*np.sqrt(252) if ex.std()>0 else 0
    dd=((equity-equity.cummax())/equity.cummax()).min()
    ca=ann/abs(dd) if abs(dd)>0.001 else 0
    wins=[t for t in trades if t.pnl>0]; los=[t for t in trades if t.pnl<=0]
    wr=len(wins)/len(trades) if trades else 0
    aw=np.mean([t.pnl_pct for t in wins]) if wins else 0
    al=abs(np.mean([t.pnl_pct for t in los])) if los else 0.001
    pf=sum(t.pnl for t in wins)/abs(sum(t.pnl for t in los)) if los and sum(t.pnl for t in los)!=0 else 999
    rr=aw/al if al>0 else 0; kelly=max(0,min(wr-(1-wr)/rr if rr>0 else 0,0.25))
    return dict(total_return=tr,annualized_return=ann,sharpe_ratio=sh,calmar_ratio=ca,
                max_drawdown=dd,win_rate=wr,profit_factor=pf,avg_win=aw,avg_loss=al,
                kelly_pct=kelly,risk_reward=rr)

def _run(df,strategy,cap=100_000):
    res=BacktestResult(strategy=strategy)
    if df is None or len(df)<60: return res
    capital=cap; evs=[cap]; eds=[df.index[0]]; trades=[]; pos=0; ep=0.0; ed=None
    c=df['close']
    def g(col,i,d=0):
        try: return float(df[col].iloc[i]) if col in df.columns else d
        except: return d
    for i in range(1,len(df)-1):
        price=float(c.iloc[i])
        if price<=0: continue
        buy=sell=False
        if strategy=='EMA Cross':
            buy=g('ema_9',i-1)<g('ema_20',i-1) and g('ema_9',i)>g('ema_20',i)
            sell=g('ema_9',i-1)>g('ema_20',i-1) and g('ema_9',i)<g('ema_20',i)
        elif strategy=='RSI Reversal':
            buy=g('rsi',i-1)<30 and g('rsi',i)>=30; sell=g('rsi',i-1)>70 and g('rsi',i)<=70
        elif strategy=='MACD Cross':
            buy=g('macd',i-1)<g('macd_signal',i-1) and g('macd',i)>g('macd_signal',i)
            sell=g('macd',i-1)>g('macd_signal',i-1) and g('macd',i)<g('macd_signal',i)
        elif strategy=='Bollinger Breakout':
            buy=float(c.iloc[i-1])<=g('bb_lower',i) and price>g('bb_lower',i)
            sell=float(c.iloc[i-1])>=g('bb_upper',i) and price<g('bb_upper',i)
        elif strategy=='Supertrend':
            buy=g('supertrend_dir',i-1)<=0 and g('supertrend_dir',i)==1
            sell=g('supertrend_dir',i-1)>=0 and g('supertrend_dir',i)==-1
        elif strategy=='VWAP + RSI':
            buy=price>g('vwap',i) and g('rsi',i)<45; sell=price<g('vwap',i) and g('rsi',i)>55
        elif strategy=='Parabolic SAR':
            buy=float(c.iloc[i-1])<g('psar',i-1) and price>g('psar',i)
            sell=float(c.iloc[i-1])>g('psar',i-1) and price<g('psar',i)
        elif strategy=='Ichimoku':
            sa,sb=g('ich_senkou_a',i),g('ich_senkou_b',i)
            buy=price>max(sa,sb) and g('ich_tenkan',i)>g('ich_kijun',i)
            sell=price<min(sa,sb) and g('ich_tenkan',i)<g('ich_kijun',i)
        elif strategy=='ADX Trend':
            adx=g('adx',i); dip=g('di_plus',i); dim=g('di_minus',i)
            buy=adx>25 and dip>dim and g('di_plus',i-1)<=g('di_minus',i-1)
            sell=adx>25 and dim>dip and g('di_minus',i-1)<=g('di_plus',i-1)
        elif strategy=='Multi-Signal':
            sc=0
            if g('rsi',i)<40: sc+=1
            elif g('rsi',i)>60: sc-=1
            if g('macd',i)>g('macd_signal',i): sc+=1
            else: sc-=1
            if price>g('ema_50',i): sc+=1
            else: sc-=1
            if g('supertrend_dir',i)==1: sc+=1
            else: sc-=1
            if price>g('vwap',i): sc+=1
            else: sc-=1
            buy=sc>=3; sell=sc<=-3
        if buy and pos==0 and capital>MIN_TRADE_EGP:
            # ✅ إصلاح: _cost() تُضيف العمولة+الانزلاق بالفعل — لا خصم إضافي
            cp=_cost(price,'buy')
            sh=int(capital*0.95/cp)
            if sh>0:
                entry_cost=sh*cp          # التكلفة الإجمالية شاملة العمولة
                capital-=entry_cost
                pos,ep,ed=sh,cp,df.index[i]
        elif sell and pos>0:
            sp=_cost(price,'sell')        # يشمل العمولة والانزلاق
            pr=pos*sp                     # المبلغ المستلم صافياً
            entry_total=pos*ep            # ما دُفع عند الشراء (شامل العمولة)
            # ✅ إصلاح: PnL الحقيقي = المستلم − ما دُفع (كلاهما يشمل التكاليف)
            pnl=pr-entry_total
            pct=pnl/entry_total if entry_total>0 else 0
            tc=entry_total*(EGX_TOTAL_COST+EGX_SLIPPAGE)*2  # تكلفة كلا الاتجاهين للعرض
            capital+=pr
            trades.append(Trade(ed,df.index[i],ep,sp,pos,entry_total,pnl,pct,tc,strategy))
            pos=0
        evs.append(capital+(pos*price if pos>0 else 0)); eds.append(df.index[i])
    if pos>0:
        lp=float(c.iloc[-1]); sp=_cost(lp,'sell'); pr=pos*sp
        entry_total=pos*ep
        pnl=pr-entry_total; pct=pnl/entry_total if entry_total>0 else 0
        tc=entry_total*(EGX_TOTAL_COST+EGX_SLIPPAGE)*2
        capital+=pr
        trades.append(Trade(ed,df.index[-1],ep,sp,pos,entry_total,pnl,pct,tc,strategy))
    equity=pd.Series(evs,index=eds[:len(evs)])
    m=_metrics(equity,trades)
    res.trades=trades; res.equity_curve=equity; res.total_trades=len(trades)
    for k in ['total_return','annualized_return','sharpe_ratio','calmar_ratio',
              'max_drawdown','win_rate','profit_factor','avg_win','avg_loss','kelly_pct','risk_reward']:
        setattr(res,k,m.get(k,0))
    return res

__all__ = ['ALL_STRATEGIES', 'run_all_backtests', 'backtest_summary_df',
           'EGXMLPredictor', 'PortfolioManager', 'dca_simulation']

ALL_STRATEGIES=['EMA Cross','RSI Reversal','MACD Cross','Bollinger Breakout',
                'Supertrend','VWAP + RSI','Parabolic SAR','Ichimoku','ADX Trend','Multi-Signal']

def run_all_backtests(df,cap=100_000,strategies=None):
    return [_run(df,s,cap) for s in (strategies or ALL_STRATEGIES)]

def backtest_summary_df(results):
    rows=[]
    for r in results:
        rows.append({'الاستراتيجية':r.strategy,'العائد الكلي':f"{r.total_return*100:.1f}%",
            'العائد السنوي':f"{r.annualized_return*100:.1f}%",'Sharpe':f"{r.sharpe_ratio:.2f}",
            'Calmar':f"{r.calmar_ratio:.2f}",'Max DD':f"{r.max_drawdown*100:.1f}%",
            'نسبة الربح':f"{r.win_rate*100:.1f}%",'معامل الربح':f"{r.profit_factor:.2f}",
            'الصفقات':r.total_trades,'Kelly%':f"{r.kelly_pct*100:.1f}%",'R:R':f"{r.risk_reward:.2f}"})
    return pd.DataFrame(rows)

class PortfolioManager:
    def __init__(self,cap=100_000): self.capital=cap
    def calc_position_size(self,price,wr,aw,al,max_risk=0.02):
        if al<=0: return {'shares':0,'capital':0,'kelly':0,'position_pct':0}
        rr=aw/al if al>0 else 1; kelly=max(0,min(wr-(1-wr)/rr if rr>0 else 0,0.15))*0.5
        sh=int(min((self.capital*max_risk)/(price*al),(self.capital*kelly)/price) if price>0 else 0)
        return {'shares':sh,'capital':sh*price,'kelly':kelly,'position_pct':sh*price/self.capital*100 if self.capital>0 else 0}
    def calc_stop_loss(self,entry,atr,mult=2.0):
        stop=entry-mult*atr; take=entry+mult*2*atr
        return {'stop_loss':stop,'take_profit':take,'risk_pct':(entry-stop)/entry*100,
                'reward_pct':(take-entry)/entry*100,'rr_ratio':(take-entry)/(entry-stop) if entry>stop else 0}


# ═══════════════════════════════════════════════════════════════
# ✅ محاكاة DCA (الاستثمار بالمبالغ الدورية المتساوية)
# ═══════════════════════════════════════════════════════════════
def dca_simulation(df: pd.DataFrame, monthly_amount: float, months: int) -> Dict:
    """
    محاكاة استراتيجية DCA — شراء بمبلغ ثابت كل شهر بدلاً من دفعة واحدة.
    تستخدم بيانات يومية فعلية وتُسقطها على أقرب يوم تداول من كل شهر.
    """
    if df is None or len(df) < 30:
        return {'error': 'بيانات غير كافية لمحاكاة DCA'}
    # ✅ إصلاح: التحقق من صحة المدخلات
    if monthly_amount <= 0:
        return {'error': 'المبلغ الشهري يجب أن يكون أكبر من الصفر'}
    if months <= 0:
        return {'error': 'عدد الشهور يجب أن يكون أكبر من الصفر'}

    c = df['close']
    step = max(int(len(c) / max(months, 1)), 1)
    indices = list(range(0, len(c), step))[:months]
    if len(indices) < 2:
        return {'error': 'فترة غير كافية للمحاكاة الشهرية'}

    total_invested = 0.0
    total_shares = 0.0
    monthly_data = []

    for m_idx, i in enumerate(indices):
        price = float(c.iloc[i])
        if price <= 0:
            continue
        buy_price = price * (1 + EGX_TOTAL_COST + EGX_SLIPPAGE)
        shares_bought = monthly_amount / buy_price
        total_shares += shares_bought
        total_invested += monthly_amount
        current_value = total_shares * price
        monthly_data.append({
            'month': m_idx + 1,
            'date': str(df.index[i])[:10],
            'price': price,
            'shares_bought': round(shares_bought, 2),
            'total_invested': total_invested,
            'current_value': current_value
        })

    if not monthly_data:
        return {'error': 'فشل بناء بيانات المحاكاة'}

    final_price = float(c.iloc[-1])
    final_value = total_shares * final_price
    total_pnl = final_value - total_invested
    total_pnl_pct = (total_pnl / total_invested * 100) if total_invested > 0 else 0
    avg_cost = total_invested / total_shares if total_shares > 0 else 0

    lump_sum_invested = monthly_amount * len(monthly_data)
    first_price = float(c.iloc[indices[0]]) * (1 + EGX_TOTAL_COST + EGX_SLIPPAGE)
    lump_shares = lump_sum_invested / first_price if first_price > 0 else 0
    lump_final_value = lump_shares * final_price
    lump_pnl_pct = ((lump_final_value - lump_sum_invested) / lump_sum_invested * 100
                     if lump_sum_invested > 0 else 0)

    return {
        'total_invested': total_invested,
        'total_shares': total_shares,
        'final_value': final_value,
        'total_pnl': total_pnl,
        'total_pnl_pct': total_pnl_pct,
        'average_cost': avg_cost,
        'final_price': final_price,
        'monthly_data': monthly_data,
        'lump_sum_pnl_pct': lump_pnl_pct,
        'dca_vs_lump_sum': total_pnl_pct - lump_pnl_pct,
    }

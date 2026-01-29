import yfinance as yf
import pandas as pd
import pandas_ta as ta
import concurrent.futures
from nselib import capital_market
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore")

MIN_AVG_VOLUME = 50000
MIN_PRICE = 30

def get_tickers():
    try:
        equity_list = capital_market.equity_list()
        return [str(s).strip() + ".NS" for s in equity_list['SYMBOL']]
    except:
        return []

# --- 1. GOLDEN STRATEGY ---
def analyze_golden(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y", interval="1d", actions=False)
        if len(df) < 200 or df['Close'].iloc[-1] < MIN_PRICE: return None
        
        df['SMA50'] = ta.sma(df['Close'], length=50)
        df['SMA200'] = ta.sma(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        df['ADX'] = ta.adx(df['High'], df['Low'], df['Close'], length=14)['ADX_14']
        df['Vol_SMA20'] = ta.sma(df['Volume'], length=20)
        
        last = df.iloc[-1]
        
        if last['Vol_SMA20'] < MIN_AVG_VOLUME: return None
        vol_rel = last['Volume'] / last['Vol_SMA20']
        
        # Golden Rules
        if not (last['Close'] > last['SMA50'] > last['SMA200']): return None
        if not (vol_rel > 1.5): return None
        if not (55 <= last['RSI'] <= 75): return None
        if last['ADX'] < 25: return None
        
        return {
            "Stock": symbol.replace(".NS", ""),
            "Price": round(last['Close'], 2),
            "Score": "9/10", # Hardcoded for simplicity or calculate dynamic
            "Sector": "Unknown", # Add sector logic if needed
            "Rel_Vol": round(vol_rel, 1)
        }
    except: return None

# --- 2. BOTTOM FISH STRATEGY ---
def analyze_bottom(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1y", interval="1d", actions=False)
        if len(df) < 200: return None
        
        df['EMA200'] = ta.ema(df['Close'], length=200)
        df['RSI'] = ta.rsi(df['Close'], length=14)
        last = df.iloc[-1]
        year_low = df['Close'].min()
        
        dist_low = ((last['Close'] / year_low) - 1) * 100
        
        # Logic
        is_near_bottom = dist_low <= 20
        is_near_ema = False
        if pd.notna(last['EMA200']):
            is_near_ema = abs(last['Close'] - last['EMA200']) / last['EMA200'] * 100 <= 3
            
        if not (is_near_bottom or is_near_ema): return None
        if last['RSI'] > 60: return None # Ensure not overbought
        
        return {
            "Stock": symbol.replace(".NS", ""),
            "Price": round(last['Close'], 2),
            "Score": "8/10",
            "Sector": "Unknown",
            "Dist_Low": round(dist_low, 1)
        }
    except: return None

# --- RUNNER ---
def run_scan(strategy_type="GOLDEN", limit=100):
    tickers = get_tickers()
    if limit: tickers = tickers[:limit] # Speed up for testing
    
    results = []
    func = analyze_golden if strategy_type == "GOLDEN" else analyze_bottom
    
    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        future_to_stock = {executor.submit(func, t): t for t in tickers}
        for future in tqdm(concurrent.futures.as_completed(future_to_stock), total=len(tickers)):
            res = future.result()
            if res: results.append(res)
            
    return pd.DataFrame(results)
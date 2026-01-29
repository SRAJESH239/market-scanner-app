import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "market_sniper.db"

def init_db():
    """Creates the database if it doesn't exist"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    # Create table to store history
    c.execute('''CREATE TABLE IF NOT EXISTS history
                 (date TEXT, stock TEXT, strategy TEXT, price REAL, 
                  score TEXT, sector TEXT, status TEXT)''')
    conn.commit()
    conn.close()

def save_scan(df, strategy_name):
    """Saves a dataframe of stocks to the database"""
    if df is None or df.empty: return
    
    conn = sqlite3.connect(DB_NAME)
    # Add today's date
    df['date'] = datetime.now().strftime("%Y-%m-%d")
    df['strategy'] = strategy_name
    df['status'] = 'New' # Mark as new find
    
    # We only save columns that match our DB schema
    save_cols = ['date', 'Stock', 'strategy', 'Price', 'Score', 'Sector', 'status']
    
    # Rename columns to match DB if needed (case sensitive)
    df_save = df.rename(columns={"Stock": "stock", "Price": "price", "Score": "score", "Sector": "sector"})
    
    # Append to database
    try:
        df_save[save_cols].to_sql('history', conn, if_exists='append', index=False)
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        conn.close()

def get_history():
    """Reads all past data"""
    conn = sqlite3.connect(DB_NAME)
    try:
        df = pd.read_sql("SELECT * FROM history ORDER BY date DESC", conn)
        return df
    except:
        return pd.DataFrame()
    finally:
        conn.close()

# Initialize DB on first run
init_db()

import yfinance as yf

symbol = "AAPL"

# Fetch enough history, then take the last 1000 trading days
df = yf.download(symbol, period="6y", interval="1d", auto_adjust=False, progress=False)

ohlc_last_1000 = df[["Open", "High", "Low", "Close"]].tail(1000)

print(ohlc_last_1000.head())
print("Rows:", len(ohlc_last_1000))

# Optional: save to CSV
ohlc_last_1000.to_csv("AAPL_last_1000_ohlc.csv", index=True)

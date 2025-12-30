from forecasterAlgorithm import forecasterAlgorithm
from dayTokenizing_buyTechnique import Tokenizer

import pandas as pd

SIM_DAY_COUNT = 1000
AVG_PRICE_DIFF = 1
AVG_PROFIT = 1
FORECASTER_CORRECT_CHANCE = 70
 



def test():
    df = pd.read_csv("AAPL_last_1000_ohlc.csv")

    forecaster = forecasterAlgorithm(FORECASTER_CORRECT_CHANCE)
    tokenizer = Tokenizer(AVG_PRICE_DIFF)
    
    
    for day in range(SIM_DAY_COUNT):
        
        # tokenizer'a market low'u gönderilecek; kar içinde market_close

        isGuessCorrect = forecaster.guess()

        if isGuessCorrect:
            tokenizer.eod(isGuessCorrect, df["Close"] - df["Open"])

        else:
            tokenizer.eod(isGuessCorrect, df["Open"] - df["Low"])    
    
    # print("kumbara: ", tokenizer.getKumbara())
    print(tokenizer.getProfit())


if __name__ == "__main__":
    for i in range(30):
        print("test_number_", i, end=". Result = ")
        test()

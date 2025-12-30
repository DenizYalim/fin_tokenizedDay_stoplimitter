from forecasterAlgorithm import forecasterAlgorithm
from dayTokenizing_buyTechnique import Tokenizer

import pandas as pd

SIM_DAY_COUNT = 1000
AVG_PRICE_DIFF = 1
AVG_PROFIT = 1
FORECASTER_CORRECT_CHANCE = 70


def test():
    forecaster = forecasterAlgorithm(FORECASTER_CORRECT_CHANCE)
    tokenizer = Tokenizer(AVG_PRICE_DIFF)
    for _ in range(SIM_DAY_COUNT):
        
        # tokenizer'a market low'u gönderilecek; kar içinde market_close

        isGuessCorrect = forecaster.guess()
        tokenizer.eod(isGuessCorrect, AVG_PROFIT)
    
    # print("kumbara: ", tokenizer.getKumbara())
    print(tokenizer.getProfit())


if __name__ == "__main__":
    for i in range(30):
        print("test_number_", i, end=". Result = ")
        test()
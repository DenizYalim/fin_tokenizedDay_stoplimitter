import pandas as pd

SIM_DAY_COUNT = 1000
AVG_PRICE_DIFF = 1
AVG_PROFIT = 1
FORECASTER_CORRECT_CHANCE = 70
 

class forecasterAlgorithm:
    def __init__(self, chance_percent: float): 
        self.chance = chance_percent / 100.0

    def guess(self) -> bool:
        return random.random() < self.chance


class Asset:
    def __init__(self, price, sellLimit, user):
        self.price:float = price
        self.sellLimit:float = sellLimit
        self.user = user
    

class marketSim:
    def __init__(self):
        self.orders = [Asset]

    def placeOrder(self, price, user, sellLimitAmount = 0):
        self.orders.append(Asset(price, sellLimitAmount, user))

    def simulateDay(self, o,h,l,c):
        
        for order in self.orders:
            if order.sellLimit > l:
                order.user.notifySellLimitTriggered()



class User:
    def __init__(self, tokenizer:Tokenizer):
        self.tokenizer = tokenizer

    def notifySellLimitTriggered(self):
        self.tokenizer.sellLimitTriggered()

class Tokenizer:
    def __init__(self, avg_price):
        self.kumbara = []
    
    def eod(self, isCorrect: bool, price: float) -> None:
        # delta is ALWAYS defined
        fark = price if isCorrect else -price

        if fark == 0:
            return

        while self.kumbara and self.kumbara[-1] * fark < 0:   
            last = self.kumbara[-1]

            m = min(abs(last), abs(fark))

            last += m if last < 0 else -m
            fark += m if fark < 0 else -m

            if last == 0:
                self.kumbara.pop()
            else:
                self.kumbara[-1] = last

            if fark == 0:
                return

        self.kumbara.append(fark)

    def sellLimitTriggered(self, price: float) -> None:
        pass
    
    def lossNoSellLimit(self, lossAmount):


    def madeProfit(self, price: float) -> None:


    def getProfit(self):
        return sum(self.kumbara)

    def getKumbara(self):
        return self.kumbara


def test():
    df = pd.read_csv("AAPL_last_1000_ohlc.csv")

    forecaster = forecasterAlgorithm(FORECASTER_CORRECT_CHANCE)
    tokenizer = Tokenizer(AVG_PRICE_DIFF)


    for row in df.itertuples(index=False):     
        o = float(row.Open)
        h = float(row.High)
        l = float(row.Low)
        c = float(row.Close)   
        
        isGuessCorrect = forecaster.guess()

        if isGuessCorrect:
            tokenizer.eod(isGuessCorrect, row["Close"] - row["Open"])

        else:
            tokenizer.eod(isGuessCorrect, row["Open"] - row["Low"])    
    

    print(tokenizer.getProfit())


if __name__ == "__main__":
    for i in range(30):
        print("test_number_", i, end=". Result = ")
        test()

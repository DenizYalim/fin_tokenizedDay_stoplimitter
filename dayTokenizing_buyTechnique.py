
class Tokenizer():
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

    
    def getProfit(self):
        return sum(self.kumbara)

    def getKumbara(self):
        return self.kumbara
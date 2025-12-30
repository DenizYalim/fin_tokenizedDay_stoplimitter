import random
from dataclasses import dataclass
from typing import List

import pandas as pd


# ----------------------------
# Config
# ----------------------------
CSV_PATH = "AAPL_last_1000_ohlc.csv"
TRIALS = 30

FORECASTER_CORRECT_CHANCE = 70  # %
BASE_STOP_USD = 0.50            # minimum stop distance in USD
MAX_STOP_USD = 5.00             # cap stop distance in USD
PROFIT_TO_STOP_MULT = 0.02      # how strongly prior profit widens the stop


# ----------------------------
# Core components
# ----------------------------
class Forecaster:
    """
    Models 'X% chance to be correct'.
    It does NOT predict direction; it just says whether your signal was correct today.
    """
    def __init__(self, chance_percent: float, rng: random.Random):
        self.p = chance_percent / 100.0
        self.rng = rng

    def is_correct_today(self) -> bool:
        return self.rng.random() < self.p


class PnLBuckets:
    """
    Stores PnL in signed buckets and cancels opposite signs against each other.
    This preserves your stack-cancellation behavior but with clearer naming.
    """
    def __init__(self):
        self._buckets: List[float] = []

    def add(self, pnl: float) -> None:
        if pnl == 0:
            return

        delta = pnl

        # Cancel against last bucket while opposite signs exist
        while self._buckets and self._buckets[-1] * delta < 0:
            last = self._buckets[-1]
            m = min(abs(last), abs(delta))

            last += m if last < 0 else -m
            delta += m if delta < 0 else -m

            if last == 0:
                self._buckets.pop()
            else:
                self._buckets[-1] = last

            if delta == 0:
                return

        self._buckets.append(delta)

    def balance(self) -> float:
        return sum(self._buckets)

    def buckets(self) -> List[float]:
        return list(self._buckets)


class SellLimitDecider:
    """
    Decides stop-loss (sell-limit) using previous accumulated profit.
    Here: more profit => allow a wider stop (risk buffer).
    """
    def __init__(self, base_stop: float, max_stop: float, profit_mult: float):
        self.base_stop = base_stop
        self.max_stop = max_stop
        self.profit_mult = profit_mult

    def stop_price(self, open_price: float, pnl_bank: PnLBuckets) -> float:
        prior_profit = max(0.0, pnl_bank.balance())
        stop_dist = self.base_stop + self.profit_mult * prior_profit
        stop_dist = max(0.01, min(self.max_stop, stop_dist))  # keep sane bounds
        return open_price - stop_dist


@dataclass(frozen=True)
class DayOHLC:
    open: float
    high: float
    low: float
    close: float


@dataclass(frozen=True)
class DayResult:
    pnl: float
    stop_triggered: bool
    stop_price: float


class Simulator:
    """
    One long trade per day:
    - Decide stop price from prior profits (buckets).
    - If low <= stop -> exit at stop
      else -> exit at close
    - If forecaster is "correct", you take close-open (ignore the stop),
      else you take the realized result with stop protection.
    """
    def __init__(self, forecaster: Forecaster, decider: SellLimitDecider, pnl_bank: PnLBuckets):
        self.forecaster = forecaster
        self.decider = decider
        self.pnl_bank = pnl_bank

    def simulate_day(self, day: DayOHLC) -> DayResult:
        stop_price = self.decider.stop_price(day.open, self.pnl_bank)
        stop_triggered = day.low <= stop_price

        if self.forecaster.is_correct_today():
            pnl = day.close - day.open
            stop_triggered = False  # treat as "signal correct; held to close"
        else:
            exit_price = stop_price if stop_triggered else day.close
            pnl = exit_price - day.open

        self.pnl_bank.add(pnl)
        return DayResult(pnl=pnl, stop_triggered=stop_triggered, stop_price=stop_price)


# ----------------------------
# Runner
# ----------------------------
def load_ohlc(csv_path: str) -> List[DayOHLC]:
    df = pd.read_csv(csv_path)

    # Supports either with Date column or without; only needs OHLC columns.
    needed = {"Open", "High", "Low", "Close"}
    missing = needed - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")

    df = df.dropna(subset=["Open", "High", "Low", "Close"])

    days: List[DayOHLC] = []
    for row in df.itertuples(index=False):
        days.append(
            DayOHLC(
                open=float(getattr(row, "Open")),
                high=float(getattr(row, "High")),
                low=float(getattr(row, "Low")),
                close=float(getattr(row, "Close")),
            )
        )
    return days[-1000:]


def run_one_trial(days: List[DayOHLC], seed: int) -> float:
    rng = random.Random(seed)

    forecaster = Forecaster(FORECASTER_CORRECT_CHANCE, rng)
    pnl_bank = PnLBuckets()
    decider = SellLimitDecider(
        base_stop=BASE_STOP_USD,
        max_stop=MAX_STOP_USD,
        profit_mult=PROFIT_TO_STOP_MULT,
    )
    sim = Simulator(forecaster, decider, pnl_bank)

    for d in days:
        sim.simulate_day(d)

    return pnl_bank.balance()


def main() -> None:
    days = load_ohlc(CSV_PATH)

    for i in range(TRIALS):
        profit = run_one_trial(days, seed=i)
        print(f"test_number_{i}. Result = {profit:.4f}")


if __name__ == "__main__":
    main()

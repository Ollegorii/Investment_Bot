import mplfinance as mpf
class Plot:
    def __init__(self, param):
        self.__param = param # parameter of graphic(candels, close price)

    def plot_candles(self, candles):
        fig, axes = mpf.plot(candles, type='candle', mav=(20), returnfig = True)
        fig.savefig('candles.png')
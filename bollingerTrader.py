import time

from algo import Algo


class BollingerTrader_v1(Algo):
    """
    long after tuching lower Bollinger bend and cross above MA. Exit after tuching upper or lower Bollinger bend.
    Short after tuching upper Bollinger bend and cross below MA. Exit after tuching upper or lower Bollinger bend
    
    Verabiles
    - ma_window -- int() The Moving Averge number to calculate the Bollinger
    - multiplier -- difualt=2, int() The std multiplier used to create the Bollinger bands 
    - max_points_loss -- int() Set maximum loss. Close position if reach (in points)
    """
    
    def __init__(self, sym, tf, ma_window, multiplier=2):
        super().__init__(sym, tf, ma_window )
        self.multiplier = multiplier
        self.ma_window = ma_window
        self.max_points_loss = False
        self.trading_method = 'bollinger'
        self.stop_method = 'bollinger'
    
    def set_data(self):
        # call the Algo class to download price data
        self.get_data()
        
        # set parmeters for the class
        self.last_close = self.df.iloc[-1]['Close']        
        self.ma_price = self.sma(self.df ,self.ma_window)
        self.upper_bend, self.lower_bend = self.bollinger(self.df, self.ma_window)
  
        self.ma = self.ma_price

    def ma_cross(self):
        if self.ma_status == 'above':
            if self.last_close < self.ma_price:
                self.ma_status = 'under'
                return True
        elif self.ma_status == 'under':
            if self.last_close > self.ma_price:
                self.ma_status = 'above'
                return True
        return False
                
    def first_status(self):
        # set MA staus on first run
        if  self.ma_price == self.last_close:
            self.ma_status = 'above' if self.ma_price < self.df.iloc[-2]['Close'] else 'under'
        else:
            self.ma_status = 'above' if self.ma_price < self.last_close else 'under' #refer to the price (close ABOVE ma)
        
        # set trading status
        self.status = 'out'
        
    def trading_logic(self): 
        if self.last_close > self.ma_price:
            return 'long'
        elif self.last_close < self.ma_price:
            return 'short'
        else:
            return False

    def print_info(self):
        stop = '' if self.status in['out', 'wait'] else '| Stop: {:.2f} '.format(self.stop)
        print ('MA_status: {}, Status: {} {}| MA: {:.2f} | last: {:.2f}  ( {} )'.format(self.ma_status,self.status, stop, self.ma_price , self.last_close ,self.df.index[-1]))
        
    def max_loss(self, ):
        stop = abs(self.last_close - self.ma)
        if self.max_loss < stop:
            print ('Max loss of %s point too high: %s ,  Close: %s,  MA: %s' % (self.max_loss, stop,self.last_close, self.ma ))
            return True


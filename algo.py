import pandas as pd
import time
import datetime as dt

from indicators import Indicators


class data_source_class:
    # this should be your data provider
    pass

class Algo(Indicators):
    def __init__(self, sym, tf, ma_window):
        self.ma_window = ma_window
        self.stop_method = 'ma'
        self.limit_method = False
        self.sym = sym
        self.tf = tf
        self.trading_status = True
        self.directoin = 'all'
        self.data_source = data_source_class
        
    def get_data(self):
        """
        You need to write your code to connect to your data provider 
        I am for example use Binance, yahoo and IB
        This should create a self.df object 
        self.df = pd.Dataframe with 'Open', 'High', 'Low', 'Close'
        * currently I am only using Close, but will probalby use the High and low in the future
        """        
        self.df = self.data_source.get_data(self.sym, self.tf)
    
    def get_current_positon(self):
        pass
    
    def open_trade(self, price, stop, action):
        self.last_trade = {'price':price, 'stop': stop, 'action':action}

    def trade_in(self):
        todo = self.trading_logic() 
        if todo:
            self.set_stop(todo)
            self.set_limit(todo)
            self.set_max_loss(todo)
            if self.under_max_loss():
                if todo == 'long' and self.directoin.lower() in ['all', 'long']:
                    self.go_long()
                elif todo == 'short' and self.directoin.lower() in ['all', 'short']:
                    self.go_short()
                
    def trade_out(self):
        if self.status == 'long':
            self.exit_long()
        elif self.status == 'short':
            self.exit_short()
        self.status = 'out'
    
    def go_long(self):        
        amount = 1
        commission = -0.52
        enter = self.last_close
        self.status = 'long'
        self.record_trades(amount, commission, enter, self.stop, 'o_long', self.limit, self.max_loss)   
        if self.trading_status:
            if self.use == 'ibrk':
                self.ibrk.buy_order(self.con, amount)
        
    def exit_long(self):
        amount = -1
        commission = -0.52
        exit = self.last_close
        self.status = 'out'
        stop = 0
        self.record_trades(amount, commission, exit, stop, 'e_long')
        if self.trading_status:
            if self.use == 'ibrk':
                self.ibrk.sell_order(self.con, amount)
      
    def go_short(self):
        amount = -1
        commission = -0.52
        enter = self.last_close
        self.status = 'short'
        self.record_trades(amount, commission, enter, self.stop,  'o_short', self.limit, self.max_loss) 
        if self.trading_status:
            if self.use == 'ibrk':
                self.ibrk.sell_order(self.con, amount)  
       
    def exit_short(self):
        amount = 1
        commission = -0.52
        exit = self.last_close
        self.status = 'out'
        stop = 0
        self.record_trades(amount, commission, exit, stop, 'e_short')
        if self.trading_status:
            if self.use == 'ibrk':
                self.ibrk.buy_order(self.con, amount)                        
                        
    def set_stop(self, direction):
        if self.stop_method.lower() == 'ma':
            self.stop = self.ma
        elif self.stop_method.lower() == 'pivot':
            if direction == 'long':
                self.stop = self.low_pivot
            elif direction == 'short':
                self.stop = self.high_pivot
        elif self.stop_method.lower() == 'bollinger':
            if direction == 'long':
                self.stop = self.lower_bend
            elif direction == 'short':
                self.stop = self.upper_bend
        elif self.stop_method.lower() == 'bollinger_revers':
            if direction == 'long':
                self.stop = self.lower_bend - self.std
            elif direction == 'short':
                self.stop = self.upper_bend + self.std
                
    def set_limit(self, direction):
        if self.limit_method:
            if self.limit_method == 'bollinger':
                # check if there is uppper and lower bend
                if not hasattr(self,'upper_bend'):
                    self.upper_bend, self.lower_bend = self.bollinger(self.df, self.ma_window)
                self.limit = self.upper_bend if direction == 'long' else self.lower_bend
            else:
                if isinstance(self.limit_method, int):
                    x = self.limit_method
                elif isinstance(self.limit_method, str):
                    x = int(''.join(number for number in self.limit_method if number.isdigit()))
                points = abs(self.last_close - self.stop) * x 
                self.limit = self.last_close + points if self.status == 'long' else self.last_close - points    
                
            assert self.limit
        else:
            self.limit = False

    def set_max_loss(self, direction):
        if self.max_points_loss:
            if isinstance(self.max_points_loss, int):
                    max_points_lost = self.max_points_loss
            if isinstance(self.max_points_loss, str) and '%' in self.max_points_loss:
                    max_points_lost = int(''.join(number for number in self.limit_method if number.isdigit())) / 100 * self.last_close
            self.max_loss = self.last_close - max_points_lost if self.status == 'long' else self.last_close + max_points_lost
        else:
            self.max_loss = False
            
    def max_loss_triger(self):
        if self.max_loss:
            if self.status.lower() == 'long' and self.last_close < self.max_loss:
                return True
            elif self.status.lower() == 'short' and self.last_close > self.max_loss:
                return True     
            else:
                return False
        else:
            False

    def under_max_loss(self):
        if self.max_loss:
            if abs(self.last_close - self.stop) > abs(self.last_close - self.max_loss):
                print ('Stop of %s too high, max point loss: %s  (stop: %s, last Close: %s)' % (abs(self.last_close - self.stop), self.max_points_loss, self.stop, self.last_close))
                return False
            else:
                return True
        else:
            return True
        
    def stop_triger(self):
        if self.status.lower() == 'long' and self.last_close < self.stop:
            return True
        elif self.status.lower() == 'short' and self.last_close > self.stop:
            return True     
        else:
            return False
    
    def limit_triger(self):
        if self.limit:
            if self.status.lower() == 'long' and self.last_close > self.limit:
                return True
            elif self.status.lower() == 'short' and self.last_close < self.limit:
                return True     
            else:
                return False
        else:
            return False
        
    def current_position(self):
        # set first position status
        # check if there is open positoin for the symbol in ibrk
        if self.trading_status:
            if self.use == 'ibrk':
                open_posiitons = self.ibrk.sym_position(self.sym)
                if len(open_posiitons) > 1:
                    if open_posiitons[1] != 0:
                        self.status = open_posiitons[0]
                        self.stop = self.ma
                        self.last_trade = {
                        'commission':0.52,
                        'open price': open_posiitons[1],
                        'stop': 0.001
                        }
                        print ('Posiiton:', self.status)

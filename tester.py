import time
import pandas as pd
pd.options.mode.chained_assignment = None


def sample_df(df, sample_to_use):
    if sample_to_use.lower() in ['weekly', 'monthly']:
        sample_to_use = sample_to_use.lower()[0]
    
    _df = pd.DataFrame()
    for col in ['x_range', 'Open', 'Date']:
        if col in df.columns:
            _df[col] = df[col].resample(sample_to_use).first()
    if 'High' in df.columns:
        _df["High"] = df["High"].resample(sample_to_use).max()
    if 'Low' in df.columns:
        _df["Low"] = df["Low"].resample(sample_to_use).min()
    if 'Close' in df.columns:
        _df["Close"] = df["Close"].resample(sample_to_use).last()
    if 'Volume' in df.columns:
        _df["Volume"] = df["Volume"].resample(sample_to_use).sum()
    _df.dropna(inplace=True)
    return _df


class Tester():
    def __init__(self, sym, tf):
        print ('Tester Start')
        self.use = None
        #if self.use is None:
        #    self.use = input('Where to get data ?(binance, ibrk, yahoo) ')
        self.sym = sym
        self.tf = tf
        self.n = 100
        self.result_dic = {}
        self.number_of_trades = 0
        self.events = {}
        #self.load_test_data()
        
    def load_test_data(self):
        # This function can be used to load the test data from local machine or online.
        # I am just loading the test data to df and than do: 
        # backtest = Tester()
        # backtest.df = df
        pass
    
    def get_data(self, sym, tf):
        self.n += 1
        if self.n % 10000 == 0:
            print ('n:', self.n)
        return self.df.iloc[:self.n]
    
    def record_trades(self, amount, commission, price, stop, action, limit='', max_loss=''):
        direction = action[2:]
        # open a new trade
        if action[0] == 'o':
            self.result_dic[self.number_of_trades] = {
                    'open_price':price,
                    'first_stop':stop,
                    'action':action,
                    'open_date':self.df.index[self.n],
                    'open_n':self.n,
                    'direction':direction,
                    'open_action':action,
                    'limit':limit,
                    'max_loss':max_loss
                    }
            
        #close trade, record PnL
        elif action[0] == 'e':
            open_price = self.result_dic[self.number_of_trades]['open_price']
            self.result_dic[self.number_of_trades]['pnl'] = price - open_price if direction == 'long' else open_price - price
            self.result_dic[self.number_of_trades]['close_price'] = price
            self.result_dic[self.number_of_trades]['close_date'] = self.df.index[self.n]
            self.result_dic[self.number_of_trades]['close_n'] = self.n
            self.result_dic[self.number_of_trades]['close_action'] = action
            
            self.number_of_trades += 1
        else:
            print ('Problem with actoin :', action )
            
    def record_actions(self, index, price, ma_price, ma_status, position):
        self.events[index] = {
                'price': price,
                'ma_price': ma_price,
                'ma_status': ma_status,
                'position': position
                   }
        
    def result(self):
        result_df = pd.DataFrame.from_dict(self.result_dic, orient='index')
        result_df.index = result_df['close_date']
        join_df = self.df.join(result_df)
        join_df['pnl_cumsum'] = join_df['pnl'].fillna(0).cumsum()
        return join_df
        
    def trading_result(self):
        df = pd.DataFrame.from_dict(self.result_dic, orient='index')
        df.index = df['close_date']
        return df
    
    def reset(self):
        self.n = 100
        self.result_dic = {}
        self.number_of_trades = 0
        print ('Backtest functions reset, ready!')


def run_test(trading_alog, n):
    trading_alog.set_data()
    trading_alog.first_status()
    trading_alog.current_position()    
    
    for i in range(n):
        trading_alog.set_data()
        if trading_alog.status == 'wait':
            trading_alog.first_status()
        
        if trading_alog.status == 'out':
            if trading_alog.ma_cross():
                trading_alog.trade_in()
            
        elif trading_alog.status in ['long', 'short']:            
            trading_alog.set_limit(trading_alog.status)
            trading_alog.set_stop(trading_alog.status)
            trading_alog.set_max_loss(trading_alog.status)
            
            if trading_alog.stop_triger() or trading_alog.limit_triger() or trading_alog.max_loss_triger():
                trading_alog.trade_out()
    print (time.ctime(),' - Finish')

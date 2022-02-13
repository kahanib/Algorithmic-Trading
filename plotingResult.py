import matplotlib.pyplot as plt
from pandas.plotting import register_matplotlib_converters
register_matplotlib_converters()

from indicators import Indicators

ind = Indicators()

class Charts():
    def __init__(self):
        self.return_plots = False
        self.figsize = (10,6)
    
    def plot_pnl_and_close(self, df, use_percent=False):
        fig, [ax1, ax2] = plt.subplots(2, sharex=True, figsize=(self.figsize))
        ax1.yaxis.tick_right()
        ax2.yaxis.tick_right()
        ax1.plot(df['Close'], drawstyle="steps")
        if use_percent:
            df['pnl_percent'] = ((df.pnl / df.open_price) + 1)
            df['pnl_percent'].fillna(1, inplace=True)
            ax2.plot(df['pnl_percent'].cumprod(), drawstyle="steps")
            if df['pnl_percent_cumprod'].max() > 0 > df['pnl_percent_cumprod'].min():
                ax2.axhline(y=0, xmin=0, xmax=1, color='k', linewidth=1, linestyle='dotted')
        else:
            ax2.plot(df['pnl_cumsum'], drawstyle="steps")
            if df['pnl_cumsum'].max() > 0 > df['pnl_cumsum'].min():
                ax2.axhline(y=0, xmin=0, xmax=1, color='k', linewidth=1, linestyle='dotted')
        
    def trades_as_box(self, df):
        fig, ax = plt.subplots(1, figsize=(self.figsize))
        ax.yaxis.tick_right()
        i = 0
        for trade in df[df['close_price'].notnull()].to_dict(orient='records'):
            highest = df.loc[trade['open_date']:trade['close_date']]['High'].max()        
            lowest = df.loc[trade['open_date']:trade['close_date']]['Low'].min()
            open_price = trade['open_price']
            max_point = highest - open_price if trade['direction'] == 'long' else open_price - lowest 
            min_point = lowest - open_price if trade['direction'] == 'long' else open_price - highest 
            color = 'blue' if trade['direction'] == 'long' else 'orange'
            plt.bar(i, trade['pnl'], color=color, width=0.5)
            plt.plot([i, i], [max_point, min_point], color='black')
            i +=1
        plt.axhline(y=0, xmin=0, xmax=1, color='k', linewidth=1)
        
    def hist(self, df,  use_percent=True):
        df = df[df.notna()].copy()
        fig, ax = plt.subplots(1)
        ax.yaxis.tick_right()
        if use_percent:
            df['pnl_percent'] = (df.pnl / df.open_price)
            df['pnl_percent'].hist(bins=100, figsize=(self.figsize))
        else: 
            df['pnl'].hist(bins=100, figsize=(self.figsize))

    def plot_trades(self, df, show='both', ma=False, bollinger=False):
        if ma:
            if isinstance(ma, int):
                df = ind.sma(df, ma, return_df=True)
            else:
                fast, slow = ma
                df = ind.sma(df, fast, return_df=True)
                df['fast_ma'] = df['ma_price']
                df = ind.sma(df, slow, return_df=True)
        if bollinger:
            df = ind.bollinger(df, bollinger, return_df=True)
            
        fig, ax = plt.subplots(1, figsize=(self.figsize))
        ax.yaxis.tick_right()
        plt.plot(df['Close'],  drawstyle="steps")
        
        if 'lower_bend' in df.columns:
            plt.plot(df['lower_bend'],  color='orange', linewidth=1, linestyle='dotted')
            plt.plot(df['upper_bend'],  color='orange', linewidth=1, linestyle='dotted')
            
        if 'ma_price' in df.columns:
            plt.plot(df['ma_price'],  color='black', linewidth=1, linestyle='dotted')
            
        if 'fast_ma' in df.columns:
            plt.plot(df['fast_ma'],  color='gray', linewidth=1, linestyle='dotted')
            
        if show == 'both':
            actions = ['open', 'close']
        if show.lower() == 'open':
            actions = ['open']
        if show.lower() == 'close':
            actions = ['close']
                    
        for trade in df[df['close_price'].notnull()].to_dict(orient='records'):
            for action in actions:
                event_marker = '^' if trade[action+'_action'] in ['o_long', 'e_short'] else 'v'
                color = 'black' if trade[action+'_action'] in ['o_long', 'o_short'] else 'red' if trade['pnl'] < 0 else 'green'
                ax.plot(trade[action+'_date'], trade[action+'_price'], event_marker, color=color)
           
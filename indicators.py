class Indicators:
    def __init__(self):
        pass

    def sma(self, df, ma_window, return_df=False):
        df['ma_price'] = df['Close'].rolling(window=ma_window).mean()
        if return_df:
            return df
        else:
            return df['ma_price'].tolist()[-1]

    def bollinger(self, df, ma_window, multiplier=2, return_df=False):
        df['ma_price'] = df['Close'].rolling(window=ma_window).mean()
        df['std'] = df['Close'].rolling(window=ma_window).std()
        df['lower_bend'] = df['ma_price'] - df['std'] * multiplier
        df['upper_bend'] = df['ma_price'] + df['std'] * multiplier
        if return_df:
            return df
        else:
            return df['upper_bend'].tolist()[-1], df['lower_bend'].tolist()[-1]

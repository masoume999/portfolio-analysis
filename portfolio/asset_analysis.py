import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, coint
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as st
import yfinance as yf
import io, base64

from .models import Asset

class LoadData():
    data = pd.DataFrame()
    def __init__(self, start_date, end_date, interval, symbols):
        self.start_date = start_date
        self.end_date = end_date
        self.asset_symbols = symbols
        self.interval = interval
        self.data = yf.download(self.asset_symbols, self.start_date, self.end_date, self.interval, group_by='ticker')

    def plot_price(self, symbol):
        price = self.data[symbol]['Close']
        plt.figure(figsize=(10, 5))
        plt.plot(price)
        # plt.title('%s' % symbol, fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel('Price', fontsize=12)

        print('Done!')
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.clf()
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

class Statistics():
    return_data = pd.DataFrame()

    def __init__(self, asset, data, window_size):
        self.asset = asset
        self.window_size = window_size
        self.data = data
        self.return_data = data.pct_change().dropna()

    def perform_statistics(self):
        returns = self.return_data
        window = self.window_size
        asset = self.asset
        stats = pd.DataFrame(index=returns.index, columns=returns.columns)
        stats['mean'] = returns[asset].rolling(window=window).mean().dropna()
        stats['var'] = returns[asset].rolling(window=window).var().dropna()
        stats['hv'] = returns.rolling(window=window).std().dropna()
        stats['skew'] = returns[asset].rolling(window=window).skew().dropna()
        stats['kurt'] = returns[asset].rolling(window=window).kurt().dropna()
        return stats

    def perform_adf_test(self):
        returns = self.return_data
        asset = self.asset
        result = adfuller(returns[asset])
        is_stationary = result[1] < 0.05
        return is_stationary

    def show_statistics(self, statistic):
        asset_name = self.asset
        plt.plot(statistic[asset_name], label=f'{asset_name}')
        plt.title('Rolling %s of Returns' % (asset_name), fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel(asset_name, fontsize=12)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=60)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def plot_corr_matrix(self):
        rolled = self.return_data.rolling(window=self.window_size)
        corr_with_target = rolled.corr().loc[:, (slice(None), self.asset)]
        corr_matrix = corr_with_target.droplevel(1, axis=1)
        plt.figure(figsize=(10, 6))
        sns.heatmap(corr_matrix, cmap='coolwarm', annot=True, fmt=".2f", linewidths=0.5)
        plt.title('Rolling Correlation with %s', (self.asset))
        plt.tight_layout()

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def get_cointegrated_assets(self):
        asset = self.asset
        symbols = self.data.columns.tolist().remove(asset)
        returns = self.return_data
        results = []
        for symbol in symbols:
            score, pvalue, _ = coint(returns[asset], returns[symbol])
            results.append((symbol, pvalue))
        cointegrated = [sym for sym, p in results if p < 0.05]
        return cointegrated

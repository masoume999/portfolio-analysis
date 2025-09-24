import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import adfuller, coint
import matplotlib
# from sympy.plotting.intervalmath import interval

matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns
import scipy.stats as st
import yfinance as yf
import io, base64
from statsmodels.tsa.vector_ar.vecm import coint_johansen

from .models import Asset

class LoadData():
    data = pd.DataFrame()
    def __init__(self, start_date, end_date, interval):
        self.start_date = start_date
        self.end_date = end_date
        self.asset_symbols = list(Asset.objects.values_list('symbol', flat=True))
        self.interval = interval
        self.data = yf.download(self.asset_symbols, start=self.start_date, end=self.end_date, interval=self.interval)['Close']

    def plot_price(self, symbol):
        price = self.data[symbol]
        plt.figure(figsize=(10, 5))
        plt.plot(price)
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

    def __init__(self, symbol, data, window_size):
        self.symbol = symbol
        self.window_size = window_size
        # self.data = data[symbol]['Close']
        self.return_data = data.pct_change().dropna()

    def perform_statistics(self):
        symbol = self.symbol
        window = self.window_size
        returns = self.return_data[symbol]
        stats = pd.DataFrame(index=returns.index)
        stats['Mean'] = returns.rolling(window=window).mean().dropna()
        stats['Variance'] = returns.rolling(window=window).var().dropna()
        stats['Historical Volatility'] = returns.rolling(window=window).std().dropna()
        stats['Skewness'] = returns.rolling(window=window).skew().dropna()
        stats['Kurtosis'] = returns.rolling(window=window).kurt().dropna()
        return stats

    def perform_adf_test(self):
        returns = self.return_data[self.symbol]
        result = adfuller(returns.squeeze())
        is_stationary = result[1] < 0.05
        return is_stationary

    def plot_statistics(self, statistic, stat_name):
        plt.figure(figsize=(10, 5))
        plt.plot(statistic[stat_name], label=f'{stat_name}')
        plt.title('Rolling %s of %s Returns' % (stat_name, self.symbol), fontsize=14)
        plt.xlabel('Date', fontsize=12)
        plt.ylabel(stat_name, fontsize=12)
        plt.xticks(rotation=30)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.clf()
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def plot_corr_matrix(self):
        symbol = self.symbol
        rolled_corr = self.return_data.rolling(window=self.window_size).corr()
        corr_with_target = rolled_corr[symbol].dropna()
        corr_matrix = corr_with_target.unstack(level=1)
        if symbol in corr_matrix.columns:
            corr_matrix = corr_matrix.drop(columns=symbol)

        corr_matrix.index = corr_matrix.index.date
        plt.figure(figsize=(12, 6))
        sns.heatmap(corr_matrix.T, cmap='coolwarm', annot=False, fmt=".2f", linewidths=0.5)
        plt.title(f'Rolling Correlation with {self.symbol}')
        plt.xticks(rotation=30)
        # plt.ylabel('Other assets', fontsize=12)
        plt.locator_params(axis='x', nbins=20)

        plt.xlabel("Date")
        plt.ylabel("Ticker")

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.clf()
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def get_cointegrated_assets(self):
        asset = self.symbol
        symbols = list(Asset.objects.values_list('symbol', flat=True))
        symbols.remove(asset)
        returns = self.return_data
        results = []
        for symbol in symbols:
            score, pvalue, _ = coint(returns[asset], returns[symbol])
            results.append((symbol, pvalue))
        cointegrated = [sym for sym, p in results if p < 0.05]
        return cointegrated


class PortfolioAnalysis():
    window_size = 1
    johansen_weights = pd.DataFrame()
    portfolio_price = pd.DataFrame()
    portfolio_return = pd.DataFrame()

    def __init__(self, portfolio):
        self.portfolio = portfolio
        self.selected_assets = [asset.symbol for asset in list(portfolio.selected_assets.all())]
        self.interval = portfolio.interval
        self.start_date = portfolio.start_date
        self.end_date = portfolio.end_date
        self.data = yf.download(self.selected_assets, start=self.start_date, end=self.end_date, interval=self.interval)['Close']

    def set_window_size(self):
        interval = self.interval
        if interval == '1d':
            self.window_size = 25
        elif interval == '5d':
            self.window_size = 5
        elif interval == '1wk':
            self.window_size = 4
        elif interval == '1mo':
            self.window_size = 1
        elif interval == '3mo':
            self.window_size = 1

    def rolling_johansen_weights(self):
        self.set_window_size()
        weight_series = []
        price_data = self.data.dropna()
        window_size = min(self.window_size, len(price_data))

        for i in range(window_size, len(price_data)):
            window_prices = price_data.iloc[i - window_size:i]

            try:
                result = coint_johansen(window_prices, det_order=0, k_ar_diff=1)
                raw_weights = result.evec[:, 0]
                normalized_weights = raw_weights / sum(abs(raw_weights))

                weight_series.append({
                    'date': price_data.index[i],
                    **{asset: weight for asset, weight in zip(self.selected_assets, normalized_weights)}
                })
            except Exception as e:
                weight_series.append({
                    'date': price_data.index[i],
                    **{asset: None for asset in self.selected_assets}
                })

        weights_df = pd.DataFrame(weight_series)
        # weights_df['date'] = pd.to_datetime(weights_df['date']).dt.date
        self.johansen_weights = weights_df

    def build_portfolio_series(self):
        price = self.data.copy()
        weights = self.johansen_weights.copy()
        value_df = pd.DataFrame()
        price['date'] = pd.to_datetime(price.index)
        weights['date'] = pd.to_datetime(weights['date'])

        merged = price.merge(weights, on='date', suffixes=('_price', '_weight'))


        for asset in self.selected_assets:
            value_df[asset] = merged[f'{asset}_price'] * merged[f'{asset}_weight']

        value_df['date'] = merged['date']
        value_df['price'] = value_df[self.selected_assets].sum(axis=1)
        value_df['return'] = value_df['price'].pct_change()
        self.portfolio_price = value_df[['date', 'price']]
        self.portfolio_return = value_df[['date', 'return']].dropna()

    def plot_return(self):
        plt.figure(figsize=(10, 5))
        plt.plot(self.portfolio_return)
        plt.title("Portfolio Return", fontsize=24)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Return", fontsize=12)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=30)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.clf()
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def plot_cumulative_return(self):
        cum_returns = self.portfolio_return.cumsum()

        plt.figure(figsize=(10, 5))
        plt.plot(cum_returns)
        plt.title("Cumulative Portfolio Return", fontsize=24)
        plt.xlabel("Date", fontsize=12)
        plt.ylabel("Cumulative Return", fontsize=12)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))
        plt.xticks(rotation=30)

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.clf()
        return base64.b64encode(buffer.getvalue()).decode('utf-8')

    def plot_portfolio_return_histogram(self):
        plt.figure(figsize=(10,5))
        plt.hist(self.portfolio_return, bins=50, edgecolor='blue')
        plt.title('Portfolio Return Histogram', fontsize=12)
        plt.xlabel('Portfolio Return', fontsize=12)
        # plt.ylabel('Frequency', fontsize=14)
        plt.grid(axis='y')

        buffer = io.BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        plt.clf()
        return base64.b64encode(buffer.getvalue()).decode('utf-8')


class RiskIndicators():
    return_data = pd.DataFrame()
    max_drawdown_percentage = 0
    standard_deviation = 0
    sortino_ratio = 0
    value_at_risk = 0
    sharpe_ratio = 0

    def __init__(self, return_data):
        self.return_data = return_data

    def get_sharpe_ratio(self, asset, risk_free_rate=0.04, days=255):
        mean = asset.mean()
        std = asset.std()
        sharpe_ratio = ((mean - risk_free_rate / days) / std) * np.sqrt(days)
        self.sharpe_ratio = sharpe_ratio

    def get_max_drawdown(self, asset):
        cumulative_max = asset.cummax()
        drawdown = (asset - cumulative_max) / cumulative_max
        max_drawdown = drawdown.min()
        max_drawdown_percentage = max_drawdown * 100
        self.max_drawdown_percentage = max_drawdown_percentage

    def get_sortino_ratio(self, asset, risk_free_rate=0.04, days=255):
        down_side_returns = asset[asset < 0]
        mean = asset.mean()
        std = down_side_returns.std()
        sortino_ratio = ((mean - risk_free_rate / days) / std) * np.sqrt(days)
        self. sortino_ratio = sortino_ratio

    def portfolio_std_dev(self, weights):
        returns = self.return_data
        weights = np.array(weights)
        portfolio = np.array([returns['Index'].values, returns['Foolad'].values, returns['Fazar'].values])
        cov_matrix = np.cov(portfolio)
        portfolio_variance = np.dot(weights.T, np.dot(cov_matrix, weights))
        portfolio_std_dev = np.sqrt(portfolio_variance)
        self.standard_deviation = portfolio_std_dev

    def get_VaR(self, confidence_level=0.95):
        returns = self.return_data
        num_assets = 6
        weights = np.repeat(1 / num_assets, num_assets)
        portfolio_returns = returns.mul(weights)
        mean = portfolio_returns.mean()
        std_dev = portfolio_returns.std()
        z_score = st.norm.ppf(1 - (1 - confidence_level))
        VaR = mean - (z_score * std_dev)
        self.value_at_risk = VaR

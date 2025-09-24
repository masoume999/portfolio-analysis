from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from .models import Asset, Portfolio
from .forms import PortfolioForm, AllAssetsForm, AssetAnalysisForm
from .analysis import LoadData, Statistics, PortfolioAnalysis, RiskIndicators
from .api.views import JohansenWeightsAPI
import os
from config import settings

def home(request):
    return render(request, 'portfolio/home.html')

def create_portfolio(request):
    if request.method == "POST":
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            # portfolio.user = request.user
            portfolio.save()
            form.save_m2m()
            return redirect('my-portfolios')
    else:
        form = PortfolioForm()
    return render(request, 'portfolio/portfolio_create.html', {'form': form})

def my_portfolios(request):
    portfolios_list = Portfolio.objects.all()
    return render(request, 'portfolio/my_portfolios.html', {'portfolios_list': portfolios_list})

def portfolio_analyses(request, pk):
    portfolio = Portfolio.objects.get(pk=pk)
    portfolio_analysis = PortfolioAnalysis(portfolio)
    portfolio_analysis.rolling_johansen_weights()
    portfolio_analysis.build_portfolio_series()
    risks = {}
    charts = []

    johansen_weights = portfolio_analysis.johansen_weights
    portfolio_price = portfolio_analysis.portfolio_price
    portfolio_return = portfolio_analysis.portfolio_return
    charts.append(portfolio_analysis.plot_return())
    charts.append(portfolio_analysis.plot_cumulative_return())
    charts.append(portfolio_analysis.plot_portfolio_return_histogram())

    risk_indicators = RiskIndicators(portfolio_return['return'])
    risk_indicators.get_sharpe_ratio()
    risk_indicators.get_sortino_ratio()
    risk_indicators.get_max_drawdown()
    risk_indicators.get_VaR()
    risk_indicators.get_portfolio_std_dev()

    risks['max_drawdown_percentage'] = risk_indicators.max_drawdown_percentage
    risks['sortino_ratio'] = risk_indicators.sortino_ratio
    risks['sharpe_ratio'] = risk_indicators.sharpe_ratio
    risks['alue_at_risk'] = risk_indicators.value_at_risk
    risks['portfolio_std_dev'] = risk_indicators.portfolio_std_dev

    johansen_weights_path = os.path.join(settings.MEDIA_ROOT, 'johansen_weights.csv')
    portfolio_price_path = os.path.join(settings.MEDIA_ROOT, 'portfolio_price.csv')
    portfolio_return_path = os.path.join(settings.MEDIA_ROOT, 'portfolio_return.csv')

    johansen_weights.to_csv(johansen_weights_path, index=False)
    portfolio_price.to_csv(portfolio_price_path, index=False)
    portfolio_return.to_csv(portfolio_return_path, index=False)

    return render(request, 'portfolio/portfolio_analyses.html', {'risk_indicators': risks, 'charts':charts})

def all_assets(request):
    form = AllAssetsForm(request.POST)
    symbols = list(Asset.objects.values_list('symbol', flat=True))
    charts = {}
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        interval = form.cleaned_data['interval']
        load_data = LoadData(start_date, end_date, interval)
        for symbol in symbols:
            charts[symbol] = load_data.plot_price(symbol)

    return render(request, 'portfolio/all_assets.html', {
        'form': form, 'charts': charts, 'symbols': symbols})

def asset_analyses(request, symbol):
    form = AssetAnalysisForm(request.POST)
    charts = []
    adf_result = None
    cntg_assets = []
    if form.is_valid():
        start_date = form.cleaned_data['start_date']
        end_date = form.cleaned_data['end_date']
        interval = form.cleaned_data['interval']
        window_size = form.cleaned_data['window_size']
        load_data = LoadData(start_date, end_date, interval)
        statistics = Statistics(symbol, load_data.data, window_size)
        adf_result = statistics.perform_adf_test()
        cntg_assets = statistics.get_cointegrated_assets()
        stats = statistics.perform_statistics()
        for stat in stats.columns:
            charts.append(statistics.plot_statistics(stats, stat))
        charts.append(statistics.plot_corr_matrix())

    return render(request, 'portfolio/asset_analyses.html',
                  {'charts': charts, 'cntg_assets':cntg_assets, 'adf_result':adf_result,
                           'symbol': symbol, 'form': form})

# class PortfolioCreateView(generic.CreateView):
#     template_name = 'portfolio/portfolio_create.html'
#     form_class = PortfolioForm

# class PortfolioListView(generic.ListView):
#     model = Portfolio
#     context_object_name = 'portfolios_list'
#     template_name = 'portfolio/my_portfolios.html'
#
# class PortfolioDetailView(generic.DetailView):
#     model = Portfolio
#     context_object_name = 'portfolio'
#     template_name = 'portfolio/portfolio_analyses.html'

from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect
from django.views import generic

from .models import Asset, Portfolio
from .forms import PortfolioForm, AllAssetsForm, AssetAnalysisForm
from .analysis import LoadData, Statistics, PortfolioAnalysis

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
    df = portfolio_analysis.rolling_johansen_weights()
    return render(request, 'portfolio/portfolio_analyses.html', {'portfolio': df})

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
